# { "Depends": "py-genlayer:5jycge4q8k23462jtb0b9fyey1s9qz928sz2nbrd9mg4sxqg2qng" }
import json
import typing
import genlayer as gl


class ParametricFlightInsurance(gl.contract.Contract):
    meta: gl.storage.TreeMap[str, str]  # "owner", "next_id", "pool_balance"
    policyholder: gl.storage.TreeMap[str, str]
    flight_number: gl.storage.TreeMap[str, str]
    flight_date: gl.storage.TreeMap[str, str]
    premium: gl.storage.TreeMap[str, str]
    payout_amount: gl.storage.TreeMap[str, str]
    delay_threshold_minutes: gl.storage.TreeMap[str, str]
    status: gl.storage.TreeMap[str, str]  # "ACTIVE" | "PAID_OUT" | "NO_PAYOUT" | "INSUFFICIENT_POOL"
    last_checked_delay: gl.storage.TreeMap[str, str]

    def __init__(self):
        self.meta["owner"] = gl.message.sender_address.as_hex
        self.meta["next_id"] = "0"
        self.meta["pool_balance"] = "0"

    # --- Insurer tops up the simulated payout pool ---
    @gl.public.write
    def fund_pool(self, amount: int) -> None:
        if gl.message.sender_address.as_hex != self.meta["owner"]:
            raise gl.vm.UserError("Only owner can fund the pool")
        if amount <= 0:
            raise gl.vm.UserError("amount must be positive")

        current = int(self.meta["pool_balance"])
        self.meta["pool_balance"] = str(current + amount)

    # --- Buyer purchases a parametric policy for a specific flight ---
    @gl.public.write
    def buy_policy(
        self,
        flight_number: str,
        flight_date: str,
        premium: int,
        payout_amount: int,
        delay_threshold_minutes: int,
    ) -> str:
        if not flight_number or not flight_date:
            raise gl.vm.UserError("flight_number and flight_date are required")
        if premium <= 0 or payout_amount <= 0 or delay_threshold_minutes < 0:
            raise gl.vm.UserError(
                "premium and payout_amount must be positive, threshold must be >= 0"
            )

        policy_id = self.meta["next_id"]

        self.policyholder[policy_id] = gl.message.sender_address.as_hex
        self.flight_number[policy_id] = flight_number
        self.flight_date[policy_id] = flight_date
        self.premium[policy_id] = str(premium)
        self.payout_amount[policy_id] = str(payout_amount)
        self.delay_threshold_minutes[policy_id] = str(delay_threshold_minutes)
        self.status[policy_id] = "ACTIVE"
        self.last_checked_delay[policy_id] = "0"

        self.meta["next_id"] = str(int(policy_id) + 1)
        self.meta["pool_balance"] = str(int(self.meta["pool_balance"]) + premium)

        return policy_id

    # --- Anyone can trigger a check; validators reach consensus on the ---
    # --- flight's real-world delay via leader_fn / validator_fn         ---
    @gl.public.write
    def check_and_settle(self, policy_id: str) -> str:
        if policy_id not in self.status:
            raise gl.vm.UserError(f"policy_id '{policy_id}' not found")
        if self.status[policy_id] != "ACTIVE":
            raise gl.vm.UserError(f"policy_id '{policy_id}' already settled")

        # Read storage into locals BEFORE the nondet block (storage proxies
        # aren't accessible inside leader_fn/validator_fn).
        flight_number = self.flight_number[policy_id]
        flight_date = self.flight_date[policy_id]

        def leader_fn() -> str:
            try:
                url = f"https://www.flightaware.com/live/flight/{flight_number}"
                page_text = gl.nondet.web.render(url, mode="text")
            except Exception as e:
                return json.dumps({
                    "status": "unknown",
                    "delay_minutes": 0,
                    "error": f"Could not retrieve flight page: {e}",
                })

            prompt = f"""You are reading a live flight-tracking page for flight {flight_number}
on {flight_date}. Read the text below and determine the flight's current
status and delay in minutes.

Respond with ONLY a JSON object, no preamble, no markdown fences, in exactly
this shape:
{{"status": "on_time" or "delayed" or "cancelled" or "unknown", "delay_minutes": <integer>}}

Page content:
\"\"\"{page_text[:4000]}\"\"\""""

            response = gl.nondet.exec_prompt(prompt)
            return response.strip()

        def validator_fn(leaders_res) -> bool:
            if not isinstance(leaders_res, gl.vm.Return):
                return False
            try:
                own_result = leader_fn()
                leader_parsed = json.loads(leaders_res.calldata)
                own_parsed = json.loads(own_result)
            except Exception:
                return False
            # Status must match exactly; delay in minutes only needs to be
            # close, since independent fetches can catch slightly different
            # moments in time.
            same_status = leader_parsed.get("status") == own_parsed.get("status")
            leader_delay = int(leader_parsed.get("delay_minutes", 0) or 0)
            own_delay = int(own_parsed.get("delay_minutes", 0) or 0)
            close_enough = abs(leader_delay - own_delay) <= 15
            return same_status and close_enough

        raw_result = gl.vm.run_nondet_default(leader_fn, validator_fn)

        try:
            parsed = json.loads(raw_result)
            flight_status = parsed.get("status", "unknown")
            delay_minutes = int(parsed.get("delay_minutes", 0) or 0)
        except Exception:
            flight_status = "unknown"
            delay_minutes = 0

        if delay_minutes < 0:
            delay_minutes = 0

        self.last_checked_delay[policy_id] = str(delay_minutes)

        threshold = int(self.delay_threshold_minutes[policy_id])
        triggered = flight_status == "cancelled" or delay_minutes >= threshold

        if triggered:
            payout = int(self.payout_amount[policy_id])
            pool = int(self.meta["pool_balance"])
            if pool < payout:
                self.status[policy_id] = "INSUFFICIENT_POOL"
                return "INSUFFICIENT_POOL"
            self.meta["pool_balance"] = str(pool - payout)
            self.status[policy_id] = "PAID_OUT"
            return "PAID_OUT"
        else:
            self.status[policy_id] = "NO_PAYOUT"
            return "NO_PAYOUT"

    # --- Read-only views ---
    @gl.public.view
    def get_policy(self, policy_id: str) -> typing.Any:
        if policy_id not in self.status:
            raise gl.vm.UserError(f"policy_id '{policy_id}' not found")

        return {
            "policy_id": policy_id,
            "policyholder": self.policyholder[policy_id],
            "flight_number": self.flight_number[policy_id],
            "flight_date": self.flight_date[policy_id],
            "premium": int(self.premium[policy_id]),
            "payout_amount": int(self.payout_amount[policy_id]),
            "delay_threshold_minutes": int(self.delay_threshold_minutes[policy_id]),
            "status": self.status[policy_id],
            "last_checked_delay": int(self.last_checked_delay[policy_id]),
        }

    @gl.public.view
    def get_pool_balance(self) -> int:
        return int(self.meta["pool_balance"])

    @gl.public.view
    def get_policy_count(self) -> int:
        return int(self.meta["next_id"])

from dataclasses import dataclass
from typing import Protocol


class PaymentState(Protocol):
    """Common interface for all payment states."""
    
    def authorize(self, amount: "Payment") -> None: ...
    def refund(self, amount: "Payment") -> None: ...
    def capture(self, amount: "Payment") -> None: ...
    def fail(self, amount: "Payment") -> None: ...


@dataclass
class Payment:
    """The context: delegates state-specific behavior to the current state object."""
    
    payment_id: str
    audit: list[str]
    state: PaymentState

    def authorize(self) -> None:
        self.state.authorize(self)

    def refund(self) -> None:
        self.state.refund(self)

    def capture(self) -> None:
        self.state.capture(self)

    def fail(self) -> None:
        self.state.fail(self)

# Concrete states implement various behaviors, associated with a state of the context.    

class New:
    def authorize(self, payment: Payment) -> None:
        payment.audit.append(f"{payment.payment_id}: authorized.")
        payment.state = Authorized()

    def refund(self, payment: Payment) -> None:
        raise Exception("Cannot refund a new payment.")

    def capture(self, payment: Payment) -> None:
        raise Exception("Cannot capture a new payment.")

    def fail(self, payment: Payment) -> None:
        payment.audit.append("Payment failed.")
        payment.state = Failed()


class Authorized:
    def authorize(self, payment: Payment) -> None:
        raise Exception("Payment is already authorized.")

    def refund(self, payment: Payment) -> None:
        payment.audit.append(f"{payment.payment_id}: refunded.")
        payment.state = Refunded()

    def capture(self, payment: Payment) -> None:
        payment.audit.append(f"{payment.payment_id}: captured.")
        payment.state = Captured()

    def fail(self, payment: Payment) -> None:
        payment.audit.append("Payment failed.")
        payment.state = Failed()


class Refunded:
    def authorize(self, payment: Payment) -> None:
        raise Exception("Cannot authorize a refunded payment.")

    def refund(self, payment: Payment) -> None:
        raise Exception("Payment is already refunded.")

    def capture(self, payment: Payment) -> None:
        raise Exception("Cannot capture a refunded payment.")

    def fail(self, payment: Payment) -> None:
        raise Exception("Cannot fail a refunded payment.")
    

class Captured:
    def authorize(self, payment: Payment) -> None:
        raise Exception("Cannot authorize a captured payment.")

    def refund(self, payment: Payment) -> None:
        payment.audit.append(f"{payment.payment_id}: refunded.")
        payment.state = Refunded()

    def capture(self, payment: Payment) -> None:
        raise Exception("Payment is already captured.")

    def fail(self, payment: Payment) -> None:
        raise Exception("Cannot fail a captured payment.")


class Failed:
    def authorize(self, payment: Payment) -> None:
        raise Exception("Cannot authorize a failed payment.")

    def refund(self, payment: Payment) -> None:
        raise Exception("Cannot refund a failed payment.")

    def capture(self, payment: Payment) -> None:
        raise Exception("Cannot capture a failed payment.")

    def fail(self, payment: Payment) -> None:
        raise Exception("Payment is already failed.")


def main() -> None:
    payment = Payment(payment_id="p1", audit=[], state=New())
    payment.authorize()
    payment.capture()
    payment.refund()

    print("final state:", type(payment.state).__name__)
    print("audit: ", payment.audit)


if __name__ == "__main__":
    main()
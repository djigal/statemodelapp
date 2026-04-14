from dataclasses import dataclass, field
from typing import Protocol
from enum import Enum, auto

from sm import StateMachine

class PayStateEnum(Enum):
    NEW = auto()
    AUTHORIZED = auto()
    REFUNDED = auto()
    CAPTURED = auto()
    FAILED = auto()

class PayEventEnum(Enum):
    AUTHORIZE = auto()
    REFUND = auto()
    CAPTURE = auto()
    FAIL = auto()

@dataclass
class PaymentCtx:
    payment_id: str
    audit: list[str] = field(default_factory=list[str])


pay_sm: StateMachine[PayStateEnum, PayEventEnum, PaymentCtx] = StateMachine()


def authorize(ctx: PaymentCtx) -> None:
    ctx.audit.append(f"{ctx.payment_id}: authorized.")


def fail(ctx: PaymentCtx) -> None:
    ctx.audit.append(f"{ctx.payment_id}: failed.")


def refund(ctx: PaymentCtx) -> None:
    ctx.audit.append(f"{ctx.payment_id}: refunded.")


def capture( ctx: PaymentCtx) -> None:
    ctx.audit.append(f"{ctx.payment_id}: captured.")

pay_sm.add_transition(PayStateEnum.NEW, PayEventEnum.AUTHORIZE, PayStateEnum.AUTHORIZED, authorize)
pay_sm.add_transition(PayStateEnum.NEW, PayEventEnum.FAIL, PayStateEnum.FAILED, fail)
pay_sm.add_transition(PayStateEnum.AUTHORIZED, PayEventEnum.REFUND, PayStateEnum.REFUNDED, refund)
pay_sm.add_transition(PayStateEnum.AUTHORIZED, PayEventEnum.CAPTURE, PayStateEnum.CAPTURED, capture)
pay_sm.add_transition(PayStateEnum.AUTHORIZED, PayEventEnum.FAIL, PayStateEnum.FAILED, fail)
pay_sm.add_transition(PayStateEnum.CAPTURED, PayEventEnum.REFUND, PayStateEnum.REFUNDED, refund)


@dataclass
class Payment:
    ctx: PaymentCtx
    state: PayStateEnum = field(default=PayStateEnum.NEW)

    def handle(self, event: PayEventEnum) -> None:
        self.state = pay_sm.handle(self.state, event, self.ctx)

def main() -> None:
    payment = Payment(ctx=PaymentCtx(payment_id="1234") )

    payment.handle(PayEventEnum.AUTHORIZE)
    payment.handle(PayEventEnum.CAPTURE)
    payment.handle(PayEventEnum.REFUND)

    print("final state:", type(payment.state))
    print("audit: ", payment.ctx.audit)


if __name__ == "__main__":
    main()
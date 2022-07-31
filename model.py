from dataclasses import dataclass
from datetime import date
from typing import Optional


class OutOfStock(Exception):
    """This is a domain exception."""

    pass


@dataclass(frozen=True)
class OrderLine:
    """The OrderLine object is an value object.

    Value objects are domain objects that are uniquely identified by the
    data contained within them. Value objects are usually made immutable.
    Basically, if changing the value of any of the attributes results in
    changing what the object as a whole represents, then the object is
    a value object.

    If we change any of the attribute values, the order line will represent
    a different order.

    Value objects are said to have short-live identity.
    """

    order_id: str
    sku: str
    quantity: int


class Batch:
    """A batch is an entity.

    Entities are used to describe domain objects that have long-lived identities.
    We are able to change attribute values of the entity without changing what the
    entity as a whole represents. For example if the batch is delayed and the ETA
    changes, the batch as a whole still represents the same entity. This is known
    as having identity equality as opposed to the value equality of value objects.
    """

    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations = set()

    def __repr__(self):
        return f"<Batch {self.reference}>"

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.quantity for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.quantity


def allocate(line: OrderLine, batches: list[Batch]) -> str:
    """This is a domain service function.

    Domain service functions are used to manipulate domain objects.
    They are implemented as separate functions as they do not have
    a natural implementation as part of an entity or value object.

    """
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")

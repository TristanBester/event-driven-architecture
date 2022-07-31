from datetime import date, timedelta

import pytest

from model import Batch, OrderLine, OutOfStock, allocate


@pytest.fixture
def today():
    return date.today()


@pytest.fixture
def tomorrow(today):
    return today + timedelta(days=1)


@pytest.fixture
def later(today):
    return today + timedelta(days=10)


def test_prefers_current_stock_batches_to_shipments(tomorrow):
    in_stock_batch = Batch("in-stock-batch", "CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "CLOCK", 100, eta=tomorrow)
    line = OrderLine("id", "CLOCK", 10)

    allocate(line, [shipment_batch, in_stock_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches(today, tomorrow, later):
    earliest = Batch("early-batch", "TABLE", 100, eta=today)
    medium = Batch("medium-batch", "TABLE", 100, eta=tomorrow)
    latest = Batch("slow-batch", "TABLE", 100, eta=later)
    line = OrderLine("id", "TABLE", 10)

    allocate(line, [earliest, medium, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref(tomorrow):
    in_stock_batch = Batch("in_stock_batch_ref", "TABLE", 100, eta=None)
    shipment_batch = Batch("shipment_batch", "TABLE", 100, eta=tomorrow)
    line = OrderLine("id", "TABLE", 10)
    allocation = allocate(line, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate(today):
    batch = Batch("batch-one", "SMALL-FORK", 10, eta=today)
    line_one = OrderLine("one", "SMALL-FORK", 10)
    line_two = OrderLine("two", "SMALL-FORK", 1)

    allocate(line_one, [batch])

    with pytest.raises(OutOfStock):
        allocate(line_two, [batch])

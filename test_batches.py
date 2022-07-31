from datetime import date

import pytest

from model import Batch, OrderLine


def make_batch_and_line(sku, batch_qty, line_qty):
    batch = Batch("batch-001", sku, batch_qty, eta=date.today())
    line = OrderLine("order-ref", sku, line_qty)
    return (batch, line)


def test_allocating_to_a_batch_reduces_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 2)
    batch.allocate(line)
    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("FANCY-LAMP", 20, 2)
    assert large_batch.can_allocate(small_line) == True


def test_cannot_allocate_if_available_less_than_required():
    small_batch, large_line = make_batch_and_line("FANCY-LAMP", 2, 20)
    assert small_batch.can_allocate(large_line) == False


def test_can_allocate_if_equal_to_required():
    batch, line = make_batch_and_line("FANCY-LAMP", 2, 2)
    assert batch.can_allocate(line) == True


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("batch-001", "CHAIR", 100, date.today())
    line = OrderLine("order-1", "LAMP", 10)
    assert batch.can_allocate(line) == False


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("DESK", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18


def test_deallocate():
    batch, line = make_batch_and_line("EXPENSIVE-TABLE", 20, 2)
    batch.allocate(line)
    batch.deallocate(line)
    assert batch.available_quantity == 20


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("TABLE", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20

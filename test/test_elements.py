import unittest
from complexism.element import *
from epidag.factory import get_workshop


class EventTestCase(unittest.TestCase):
    def setUp(self):
        self.Event1 = Event('Task 1', 1)
        self.Event2 = Event('Task 2', 5)
        self.Event3 = Event('Task 3', 5)

    def test_attributes(self):
        self.assertEqual(self.Event1.Todo, 'Task 1')
        self.assertEqual(self.Event1.Time, 1)

    def test_compare(self):
        self.assertTrue(self.Event1 < self.Event2)
        self.assertFalse(self.Event1 == self.Event2)
        self.assertFalse(self.Event1 > self.Event2)

        self.assertFalse(self.Event2 < self.Event1)
        self.assertFalse(self.Event2 == self.Event1)
        self.assertTrue(self.Event2 > self.Event1)

        self.assertTrue(self.Event2 == self.Event3)
        self.assertTrue(self.Event2 >= self.Event3)
        self.assertTrue(self.Event2 <= self.Event3)
        self.assertFalse(self.Event2 is self.Event3)

    def test_null(self):
        self.assertEqual(Event.NullEvent.Time, float('Inf'))


class RequestTestCase(unittest.TestCase):
    def setUp(self):
        self.Req1 = Request(Event('Task 1', 1), 'I', 'Home')
        self.Req2 = Request(Event('Task 2', 2), 'You', 'Home')
        self.Req3 = Request(Event('Task 3', 2), 'She', 'Home')

    def test_attributes(self):
        self.assertEqual(self.Req1.What, 'Task 1')
        self.assertEqual(self.Req1.When, 1)
        self.assertEqual(self.Req1.Who, 'I')
        self.assertEqual(self.Req1.Address, 'Home')
        self.assertEqual(self.Req1.Group, 'Home')

    def test_hoist(self):
        req11 = self.Req1.up_scale('Taipei')
        self.assertEqual(req11.Address, 'Home@Taipei')

        _, req12 = req11.down_scale()
        self.assertEqual(req12.Address, 'Home')

        self.assertRaises(AttributeError, req12.down_scale)

    def test_compare(self):
        self.assertTrue(self.Req1 < self.Req2)
        self.assertFalse(self.Req1 == self.Req2)
        self.assertFalse(self.Req1 > self.Req2)

        self.assertFalse(self.Req2 < self.Req1)
        self.assertFalse(self.Req2 == self.Req1)
        self.assertTrue(self.Req2 > self.Req1)

        self.assertTrue(self.Req2 == self.Req3)
        self.assertTrue(self.Req2 >= self.Req3)
        self.assertTrue(self.Req2 <= self.Req3)
        self.assertFalse(self.Req2 is self.Req3)

        self.assertEqual(min(self.Req1, self.Req2), self.Req1)


class TickerTestCase(unittest.TestCase):
    def setUp(self):
        self.TickerLib = get_workshop('Ticker')

    def test_step(self):
        tk = self.TickerLib.from_json({'Name': '', 'Type': 'Step', 'Args': {'dt': 0.5}})
        tk.initialise(0)
        ti = tk.Next
        self.assertEqual(ti, 0.5)
        tk.update(ti)
        ti = tk.Next
        self.assertEqual(ti, 1)

    def test_schedule(self):
        tk = self.TickerLib.from_json({'Name': '', 'Type': 'Schedule',
                                      'Args': {'ts': [0.4, 0.6]}})
        tk.initialise(0)
        ti = tk.Next
        self.assertEqual(ti, 0.4)
        tk.update(ti)
        ti = tk.Next
        self.assertEqual(ti, 0.6)

    def test_appointment(self):
        tk = self.TickerLib.from_json({'Name': '', 'Type': 'Appointment',
                                       'Args': {'queue': [-5, 0.4, 0.6]}})
        tk.initialise(0)
        ti = tk.Next
        self.assertEqual(ti, 0.4)
        tk.update(ti)
        ti = tk.Next
        self.assertEqual(ti, 0.6)

        tk.make_an_appointment(0.5)
        ti = tk.Next
        self.assertEqual(ti, 0.5)

        tk.update(ti)
        tk.make_an_appointment(0.45)
        ti = tk.Next
        self.assertEqual(ti, 0.6)


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python
import unittest
from py2030.components.midi_input import MidiInput
from py2030.event_manager import EventManager

class MidiPortMock:
    def __init__(self, messages=[]):
        self.messages = messages

    def close_port(self):
        pass

    def get_message(self):
        if len(self.messages) > 0:
            return self.messages.pop(0)
        return False

class TestMidiInput(unittest.TestCase):
    def test_init(self):
        midiinput = MidiInput()
        self.assertFalse(midiinput.connected)
        self.assertIsNone(midiinput.midiin)
        self.assertIsNone(midiinput.port_name)
        self.assertIsNone(midiinput.port)
        self.assertIsNotNone(midiinput.messageEvent)
        self.assertIsNone(midiinput.event_manager)

    # commented out because they try to connec to a midi device
    def test_setup_with_event_manager(self):
        em = EventManager()
        midiinput = MidiInput()
        midiinput.setup(em, midi_port=MidiPortMock())
        self.assertEqual(midiinput.event_manager, em)

    def test_setup_without_event_manager(self):
        midiinput = MidiInput()
        midiinput.setup(midi_port=MidiPortMock())
        self.assertIsNone(midiinput.event_manager)

class TestMidiInputOutputEvents(unittest.TestCase):
    def test_no_output_events_specified(self):
        midiinput = MidiInput()
        midiinput.setup(EventManager(), midi_port=MidiPortMock([[[144,36]]]))
        midiinput.update() # process mocked midi message
        self.assertEqual(len(midiinput.event_manager._events), 0)

    def test_midi_note_triggers_event(self):
        midiinput = MidiInput({'output_events': {144: {36: 'begin'}}})
        midiinput.setup(EventManager(), midi_port=MidiPortMock([[[144,36]]]))
        self.assertEqual(midiinput.event_manager.get('begin')._fireCount, 0)
        midiinput.update() # process mocked midi message
        self.assertEqual(midiinput.event_manager.get('begin')._fireCount, 1)

    def test_midi_note_triggers_multiple_events(self):
        midiinput = MidiInput({'output_events': {144: {36: ['begin', 'middle', 'end']}}})
        midiinput.setup(EventManager(), midi_port=MidiPortMock([[[144,36]]]))
        self.assertEqual(midiinput.event_manager.get('begin')._fireCount, 0)
        self.assertEqual(midiinput.event_manager.get('middle')._fireCount, 0)
        self.assertEqual(midiinput.event_manager.get('end')._fireCount, 0)
        midiinput.update() # process mocked midi message
        self.assertEqual(midiinput.event_manager.get('begin')._fireCount, 1)
        self.assertEqual(midiinput.event_manager.get('middle')._fireCount, 1)
        self.assertEqual(midiinput.event_manager.get('end')._fireCount, 1)

    def test_midi_note_triggers_event_with_param(self):
        midiinput = MidiInput({'output_events': {144: {36: {'event': 'load', 'params': 1}}}})
        midiinput.setup(EventManager(), midi_port=MidiPortMock([[[144,36]]]))
        self.assertEqual(midiinput.event_manager.get('load')._fireCount, 0)
        midiinput.update() # process mocked midi message
        self.assertEqual(midiinput.event_manager.get('load')._fireCount, 1) # TODO verify it fired with params: [1]

    def test_midi_note_triggers_event_with_multiple_params(self):
        midiinput = MidiInput({'output_events': {144: {36: {'event': 'load', 'params': [1,2,3]}}}})
        midiinput.setup(EventManager(), midi_port=MidiPortMock([[[144,36]]]))
        self.assertEqual(midiinput.event_manager.get('load')._fireCount, 0)
        midiinput.update() # process mocked midi message
        self.assertEqual(midiinput.event_manager.get('load')._fireCount, 1) # TODO verify it fired with al three params: [1,2,3]

    def test_unknown_midi_note_triggers_nothing(self):
        midiinput = MidiInput({'output_events': {144: {36: 'begin'}}})
        midiinput.setup(EventManager(), midi_port=MidiPortMock([[[144,37]], [[145,36]]]))
        midiinput.update() # process mocked midi messages
        self.assertEqual(len(midiinput.event_manager._events), 0)

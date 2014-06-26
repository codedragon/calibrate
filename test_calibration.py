import unittest
from panda3d.core import loadPrcFileData
from direct.task.TaskManagerGlobal import taskMgr
from calibration import World
from time import time
import types
import sys

# Tests run fine one at a time, but on Windows, isn't destroying
# the ShowBase instance between suites, for some crazy reason. Meh.
# So, to run in Windows, have to comment out one suite, run once,
# change class_switch to True, run again. Switch everything back.


class TestCalibration(unittest.TestCase):
# task.time is not very accurate when running off-screen
# Need to make these tests faster. Since we are testing the logic
# of moving from one task to the next, probably easiest way is to
# override the intervals to much smaller amounts.
# codes for w.next
#            0: self.square_on,
#            1: self.square_fade,
#            2: self.square_off,
#            3: self.square_move}

    @classmethod
    def setUpClass(cls):
        print 'setup class'
        if class_switch:
            print 'class has been run for manual, switch to random'
            cls.manual = 2
        else:
            print 'first time through, run for manual'
            cls.manual = 1
        loadPrcFileData("", "window-type offscreen")
        #print 'about to load world'
        #print 'boo', cls.manual
        cls.w = World(cls.manual, 1)

    def setUp(self):
        print 'setup'
        self.config = {}
        execfile('config_test.py', self.config)
        self.w.open_files(self.config)
        self.depth = 0
        #print('setup done')

    def test_no_square(self):
        """
        Should start with a blank screen, square has no parent, not rendered.
        This happens at beginning (next = 0) and anytime when about to get reward (next = 3)
        or for random when 0 again.
        Can't guarantee this is run at beginning, but sufficient to check that square is not
        rendered for these two conditions
        """
        #print self.w.square.getParent()
        #
        if self.w.next != 0:
            square_on = True
            while square_on:
                taskMgr.step()
                #if self.w.next == 3  or self.w.next == 0:
                if self.w.next == 0:
                    square_on = False
        self.assertFalse(self.w.square.getParent())

    def test_square_turns_on(self):
        """
        The square should turn on when next is 1
        """
        #time_out = time.time() + 2.1
        #start_time =
        square_off = True
        while square_off:
        #while time.time() < time_out:
            taskMgr.step()
            # if taskTask.now changes to 1, then we have just turned on
            if self.w.next == 1:
                #print 'square should be on'
                square_off = False
        self.assertTrue(self.w.square.getParent())

    def test_square_turns_off(self):
        square_dim = True
        # with manual, we don't use 0, and for random we don't use 3...
        if self.manual == 1:
            match = 3
        else:
            match = 0
        while square_dim:
            taskMgr.step()
            if self.w.next == match:
                square_dim = False
        self.assertFalse(self.w.square.getParent())

    def test_eye_data_written_to_file(self):
        # make sure data is written to file.
        # this is a little tricky, since we don't know where the data is going to be
        # in the file, depends on where we were when we opened the file. Assume that
        # the data file was opened within the first ten time stamps
        #print('manual is', self.w.manual)
        last = self.w.next
        no_change = True
        test = 0
        while no_change:
            taskMgr.step()
            # if taskTask.now changes to 1, then we have just turned on
            if self.w.next != last:
                #print 'we did something'
                test = time()
                no_change = False

        eye_data = self.w.eye_data[:10]
        #print self.w.eye_data[:10]
        # need to stop task, so file is closed
        self.w.close()
        #print(self.w.eye_file_name)
        # since we are using fake data, know that first point is (0,0)
        f = open(self.w.eye_file_name, 'r')
        #print(f.readline())
        self.assertIn('timestamp', f.readline())
        #print('what is actually in file after timestamp line')
        my_line = f.readline()
        check_data = None
        for eye in eye_data:
            #print(eye[0])
            if str(eye[0]) in my_line:
                check_data = str(eye[0])
                break
        self.assertIn(check_data, my_line)
        # time is a floating point in seconds, so if we just
        # check to see if the digits from the 10s place on up
        # are there, we know we have a time stamp from the last
        # 10 seconds in the file, and that is good enough, we
        # know there is a time stamp, and it is unlikely that
        # one of the eye positions had these exact numbers
        # Ack, so the time stamp we get is sometimes off by a fraction
        # of a second from the one that is in the file, which means
        # that anytime the test time stamp is right at the cusp of a
        # change in the tens place, at say, 1403723090.4, and the original
        # stamp is 1403723089.42, we won't get a match if looking at the
        # tens place. We have enough digits, let's match to the 100s, which
        # still has the same problem, but is a much rarer problem.
        #
        #print test
        time_check = int(test - (test % 100)) / 100
        self.assertIn(str(time_check), f.readline())
        f.close()

    def test_tasks_and_timestamp_written_to_file(self):
        # make sure data is written to file.
        # make sure starts at moving, so will write to file even with random
        start_task = self.w.next
        #print 'start at ', start_task
        no_tasks = True
        # do at least one task
        while no_tasks:
            taskMgr.step()
            if self.w.next != start_task:
                #print 'something happened'
                no_tasks = False
        #print 'task now', self.w.next
        # need to stop task, so file is closed
        self.w.close()
        #print self.w.time_file_name
        f = open(self.w.time_file_name, 'r')
        self.assertIn('timestamp', f.readline())
        self.assertIn('start collecting', f.readline())
        test = f.readline()
        # it is possible reward is the next line, since we don't always start
        # from the beginning. If on random, won't fixate
        #print self.manual
        if start_task == 3:
            self.assertIn('Reward', test)
        elif start_task == 1 and self.manual != 1:
            self.assertIn('no fixation', test)
        else:
            self.assertIn('Square', test)

    def test_change_from_manual_to_auto_or_vise_versa(self):
        # I think it shouldn't matter if we don't switch back,
        # since everything should work either way, and we change
        # into the opposite direction the next time through
        before = self.w.manual
        self.w.switch_task = True
        # run the task long enough to switch
        square_on = True
        # if we are on zero, need to do two loops
        #if self.w.next == 0:
        #    loop = 2
        #else:
        #    loop = 1
        last = self.w.next
        #print self.w.next
        while square_on:
            taskMgr.step()
            if self.w.next != last:
                last = self.w.next
            if last == 3 or last == 0:
                square_on = False

        after = self.w.manual
        self.assertNotEqual(before, after)

    def test_change_tasks_and_positions_change(self):
        #print('manual is', self.w.manual)
        #print('type', type(self.w.pos))
        self.w.switch_task = True
        # run the task long enough to switch
        last = self.w.next
        #print self.w.next
        square_on = True
        while square_on:
            taskMgr.step()
            if self.w.next != last:
                last = self.w.next
            if last == 3 or last == 0:
                square_on = False
            #print('manual is', self.w.manual)
        #print('type', type(self.w.pos))
        if self.w.manual:
            #print('manual is instance')
            self.assertIsInstance(self.w.pos, types.InstanceType)
            #new_pos = self.w.pos.get_key_position(self.w.depth, 5)
        else:
            #print('not manual, auto is generator')
            self.assertIsInstance(self.w.pos, types.GeneratorType)
            #new_pos = self.w.pos.next()
            #print new_pos
            #switch back - not really the 'correct' way, I know...
            #self.w.change_tasks()
            #print self.w.manual

    def tearDown(self):
        self.w.clear_eyes()
        self.w.close_files()

    @classmethod
    def tearDownClass(cls):
        taskMgr.remove(cls.w.frameTask)
        cls.w.close()
        del cls.w
        print 'tore down'

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCalibration)
    class_switch = False
    if len(sys.argv) == 2:
        print 'yup'
        if sys.argv[1] == 'True':
            print 'true'
            class_switch = True
            print 'go'
        elif sys.argv[1] == 'Mac':
            class_switch = True
            # run twice to cover both conditions
            unittest.TextTestRunner().run(suite)
        print 'test'
        unittest.TextTestRunner().run(suite)
    else:
        # when you just want to the suite from the command line
        # without a sys.argv, in this case, if you want class_switch
        # to be True, must uncomment. gives you more verbosity
        #class_switch = True
        unittest.main(verbosity=2)
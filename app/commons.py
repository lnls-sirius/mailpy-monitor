import time
import typing

class Condition(object):
    OutOfRange = "out of range"
    SuperiorThan = "if superior than"
    InferiorThan = "if inferior than"
    IncreasingStep = "increasing step"
    DecreasingStep = "decreasing step"


class Entry:
    # @todo: create enable flag and enable PV string
    def __init__(self, pv, emails, condition, value, unit, warning, subject, timeout, enable):
        self.pv = pv
        self.condition = condition
        self.value = value
        self.unit = unit
        self.warning = warning
        self.subject = subject
        self.timeout = timeout
        self.enable = enable
        self.emails = emails

        # reset last_event_time for all PVs, so it start monitoring right away
        self.start_time:float = time.time()
        self.last_event_time = self.start_time - self.timeout

        if self.condition == Condition.IncreasingStep:
            self.__init_increasing_step__()

        self.step_level: int = 0                  # Actual level
        self.step_value: typing.List[float] = []  # Step value according to level


    def __init_increasing_step__(self):
        '''
         create two dictionaries, "step_level" and "step":
          -------------------------------------------------------------------------
          * step_level:
              - keys: [int] indexes that contain the 'increasing step' condition
              - values: [int] represent the current step in the stair, where 0 is
                        the lowest level, and len(step[i]) is highest level
             e.g.:
                value = '1.5:2.0:2.5:3.0'
                step  = [1.5,2.0,2.5,3.0]
                len(step) = 4

                3.0 _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _  ___Level_4___
                2.5 _ _ _ _ _ _ _ _ _ _ _ _ _ _ __L3__|
                2.0 _ _ _ _ _ _ _ _ _ _  __L2__|
                1.5 _ _ _ _ _ _ _ __L1__|
                                 |
                                 |
                  0 ___Level_0___|

               -Level 0: lowest level, 0 ~ 1.5 u (normal operation)
                  ...
               -Level 4: highest level, 3.0+

           obs.: emails are only sent when moving from any level to a higher one
          -------------------------------------------------------------------------
          * step:
              - keys: [int] indexes that contain the 'increasing step' condition
              - values: [array of float] represent the steps that triggers mailing
        '''
        self.step_level = 0
        self.step_value = [float(val) for val in self.value.split[':']]

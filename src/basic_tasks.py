"""!
@file basic_tasks.py
    This file contains a program with two tasks. The first task reads data from the accelerametor
    twice per second and loads into a shared queue value. This queue is then printed
    by the second task.
@author MECHE-07
@date   2023-2-17
@copyright (c) 2023 by Mech-07 and JR Ridgely and released under GNU Public License v3
"""

import gc
import pyb
import cotask
import task_share
import mma845x
import micropython

## The register address of the STATUS register in the MMA845x
STATUS_REG = micropython.const (0x00)

## The register address of the OUT_X_MSB register in the MMA845x
OUT_X_MSB = micropython.const (0x01)

## The register address of the OUT_X_LSB register in the MMA845x
OUT_X_LSB = micropython.const (0x02)

## The register address of the OUT_Y_MSB register in the MMA845x
OUT_Y_MSB = micropython.const (0x03)

## The register address of the OUT_Y_LSB register in the MMA845x
OUT_Y_LSB = micropython.const (0x04)

## The register address of the OUT_Z_MSB register in the MMA845x
OUT_Z_MSB = micropython.const (0x05)

## The register address of the OUT_Z_LSB register in the MMA845x
OUT_Z_LSB = micropython.const (0x06)

## The register address of the WHO_AM_I register in the MMA845x
WHO_AM_I = micropython.const (0x0D)

## The register address of the DATA_CFG_REG register in the MMA845x which is
#  used to set the measurement range to +/-2g, +/-4g, or +/-8g
XYZ_DATA_CFG = micropython.const (0x0E)

## The register address of the CTRL_REG1 register in the MMA845x
CTRL_REG1 = micropython.const (0x2A)

## The register address of the CTRL_REG2 register in the MMA845x
CTRL_REG2 = micropython.const (0x2B)

## The register address of the CTRL_REG3 register in the MMA845x
CTRL_REG3 = micropython.const (0x2C)

## The register address of the CTRL_REG4 register in the MMA845x
CTRL_REG4 = micropython.const (0x2D)

## The register address of the CTRL_REG5 register in the MMA845x
CTRL_REG5 = micropython.const (0x2E)

## Constant which sets acceleration measurement range to +/-2g
RANGE_2g = micropython.const (0)

## Constant which sets acceleration measurement range to +/-2g
RANGE_4g = micropython.const (1)

## Constant which sets acceleration measurement range to +/-2g
RANGE_8g = micropython.const (2)

def task1_fun(shares):
    """!
    Reads the X acceleration (2 times per second)
    @param shares A list holding the share and queue used by this task
    """
    my_share, my_queue = shares
    
    address = 29
    accel = mma845x.MMA845x(pyb.I2C (1, pyb.I2C.MASTER, baudrate = 100000), address, RANGE_2g)
    accel.active()
    
    
    while not my_queue.full():
        ax = accel.get_ax_bits()
        my_share.put(ax)
        my_queue.put(ax)
        yield 0
    yield 0 

def task2_fun(shares):
    """!
    Task which prints the accelerator queue 
    @param shares A tuple of a share and queue from which this task gets data
    """
    my_share, my_queue = shares
    
    while True:
        if my_queue.any ():
            value = my_queue.get()
            print(value)
            yield 0
        yield 0 

# This code creates a share, a queue, and two tasks, then starts the tasks. The
# tasks run until somebody presses ENTER, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.
if __name__ == "__main__":
    
    queue1 = []
    
    print("Testing ME405 stuff in cotask.py and task_share.py\r\n"
          "Press Ctrl-C to stop and show diagnostics.")

    # Create a share and a queue to test function and diagnostic printouts
    share0 = task_share.Share('h', thread_protect=False, name="Share 0")
    q0 = task_share.Queue('L', 16, thread_protect=False, overwrite=False,
                          name="Queue 0")

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    task1 = cotask.Task(task1_fun, name="Task_1", priority=1, period=500,
                        profile=True, trace=False, shares=(share0, q0))
    task2 = cotask.Task(task2_fun, name="Task_2", priority=2, period=100,
                        profile=True, trace=False, shares=(share0, q0))
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break

    # Print a table of task data and a table of shared information data
    print('\n' + str (cotask.task_list))
    print(task_share.show_all())
    print(task1.get_trace())
    print('')

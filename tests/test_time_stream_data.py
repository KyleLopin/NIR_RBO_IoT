# Copyright (c) 2022 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Test the data_class.TimeStreamData class
"""

__author__ = "Kyle Vitautus Lopin"

# standard libraries
import datetime as dt
import filecmp
import json
import os
import shutil
import sys
import unittest
from unittest import mock

# installed libraries
import freezegun

sys.path.append(os.path.join('..', 'GUI'))
# local files
from GUI import data_class

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
PROJECT_DIR = os.path.abspath(os.path.join(__location__, os.pardir, 'GUI'))

TEST_DATE = "2022-11-18"
NEXT_DATE = "2022-11-19"
# SAVED_FILE_PATH = os.path.join('..', 'GUI', 'data', f"{TEST_DATE}.csv")
SAVED_FILE_PATH = os.path.join(PROJECT_DIR, 'data', f"{TEST_DATE}.csv")
TOMORROW_FILE_PATH = os.path.join(PROJECT_DIR, 'data', f"{NEXT_DATE}.csv")
TEMPLATE_FILE = os.path.join(__location__, "template_short.csv")
SORTED_TEMPLATE_FILE = os.path.join(__location__, "sorted_template_short.csv")
MISSING_AV_FILE = os.path.join(__location__, "test_mixed_av.csv")

DATA_PKT1 = b'{"time": "09:55:22", "date": "2022-11-18", "packet_id": 1, ' \
            b'"device": "position 2", "mode": "live", "OryConc": -20139, ' \
            b'"CPUTemp": "48.31", "SensorTemp": 0, "AV": -1}'
DATA_PKT2 = b'{"time": "10:05:13", "date": "2022-11-18", "packet_id": 3, ' \
            b'"device": "position 2", "mode": "live", "OryConc": -20602, ' \
            b'"CPUTemp": "48.31", "SensorTemp": "41.79", "AV": -2}'
DATA_PKT3 = b'{"time": "10:06:13", "date": "2022-11-18", "packet_id": 4, ' \
            b'"device": "position 2", "mode": "live", "OryConc": -20648, ' \
            b'"CPUTemp": "47.24", "SensorTemp": 0, "AV": -4}'
DATA_PKT_OLD = b'{"time": "10:06:13", "date": "2022-11-17", "packet_id": 4, ' \
               b'"device": "position 2", "mode": "live", "OryConc": -20648, ' \
               b'"CPUTemp": "47.24", "SensorTemp": 0, "AV": -4}'
DATA_PKT_MISSING_DEVICE = b'{"time": "10:06:13", "date": "2022-11-17", "packet_id": 4, ' \
                          b'"mode": "live", "OryConc": -20648, "CPUTemp": "47.24", ' \
                          b'"SensorTemp": 0, "AV": -42}'
DATA_PKT_NEW = b'{"time": "00:06:13", "date": "2022-11-19", "packet_id": 4, ' \
               b'"device": "position 2", "mode": "live", "OryConc": -20648, ' \
               b'"CPUTemp": "47.24", "SensorTemp": 0, "AV": -5}'
DATA_PKT_POSITION_1 = b'{"time": "23:06:13", "date": "2022-11-18", "packet_id": 46, ' \
               b'"device": "position 1", "mode": "live", "OryConc": -20648, ' \
               b'"CPUTemp": "47.24", "SensorTemp": 0, "AV": 10}'
DATA_PKT_POSITION_1_2 = b'{"time": "00:07:13", "date": "2022-11-18", "packet_id": 5, ' \
               b'"device": "position 1", "mode": "live", "OryConc": -20648, ' \
               b'"CPUTemp": "47.24", "SensorTemp": 0, "AV": 11}'
DATA_PKT_POSITION_1_NEW = b'{"time": "00:07:13", "date": "2022-11-19", "packet_id": 4, ' \
               b'"device": "position 1", "mode": "live", "OryConc": -20111, ' \
               b'"CPUTemp": "47.24", "SensorTemp": 0, "AV": 12}'
CORRECT_PACKET_IDS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                      17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44,
                      45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58,
                      59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72,
                      73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86,
                      87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100,
                      101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111,
                      112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123,
                      124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135,
                      136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147,
                      148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159,
                      160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171,
                      172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183,
                      184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195,
                      196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207,
                      208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219,
                      220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231,
                      232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243,
                      244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255,
                      256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267,
                      268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279,
                      280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291,
                      292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303,
                      304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315,
                      316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327,
                      328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339,
                      340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351,
                      352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363,
                      364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375,
                      376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387,
                      388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399,
                      400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411,
                      412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423,
                      424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435,
                      436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447,
                      448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459,
                      460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471,
                      472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483,
                      484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495,
                      496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507,
                      508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519,
                      520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531,
                      532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543,
                      544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555,
                      558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569,
                      570, 571, 572, 573, 574, 575, 576, 577, 578, 639, 640, 642,
                      643, 644, 645, 647, 649, 650, 651, 652, 654, 655, 656, 657,
                      660, 661, 662, 663, 667, 670, 671, 673, 675, 676, 677, 678,
                      679, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690,
                      691, 692, 693, 694, 695, 696, 697, 698, 699, 700, 701, 702,
                      703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 714,
                      715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726,
                      727, 728, 729, 730, 732, 733, 740, 1036, 1037, 1038, 1039,
                      1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049,
                      1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059,
                      1060, 1061, 1062, 1063, 1064, 1065, 1066, 1067, 1068, 1069,
                      1070, 1071, 1072, 1073, 1074, 1075, 1076, 1077, 1078, 1079,
                      1080, 1081, 1082, 1083, 1084, 1085, 1086, 1087, 1088]
CORRECT_PACKET_IDS = [0, 1, 2, 3, 12, 13, 21]
MISSING_PACKETS = [556, 557, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588,
                   589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600,
                   601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612,
                   613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624,
                   625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636,
                   637, 638, 641, 646, 648, 653, 658, 659, 664, 665, 666, 668,
                   669, 672, 674, 731, 734, 735, 736, 737, 738, 739, 741, 742,
                   743, 744, 745, 746, 747, 748, 749, 750, 751, 752, 753, 754,
                   755, 756, 757, 758, 759, 760, 761, 762, 763, 764, 765, 766,
                   767, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 778,
                   779, 780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 790,
                   791, 792, 793, 794, 795, 796, 797, 798, 799, 800, 801, 802,
                   803, 804, 805, 806, 807, 808, 809, 810, 811, 812, 813, 814,
                   815, 816, 817, 818, 819, 820, 821, 822, 823, 824, 825, 826,
                   827, 828, 829, 830, 831, 832, 833, 834, 835, 836, 837, 838,
                   839, 840, 841, 842, 843, 844, 845, 846, 847, 848, 849, 850,
                   851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861, 862,
                   863, 864, 865, 866, 867, 868, 869, 870, 871, 872, 873, 874,
                   875, 876, 877, 878, 879, 880, 881, 882, 883, 884, 885, 886,
                   887, 888, 889, 890, 891, 892, 893, 894, 895, 896, 897, 898,
                   899, 900, 901, 902, 903, 904, 905, 906, 907, 908, 909, 910,
                   911, 912, 913, 914, 915, 916, 917, 918, 919, 920, 921, 922,
                   923, 924, 925, 926, 927, 928, 929, 930, 931, 932, 933, 934,
                   935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946,
                   947, 948, 949, 950, 951, 952, 953, 954, 955, 956, 957, 958,
                   959, 960, 961, 962, 963, 964, 965, 966, 967, 968, 969, 970,
                   971, 972, 973, 974, 975, 976, 977, 978, 979, 980, 981, 982,
                   983, 984, 985, 986, 987, 988, 989, 990, 991, 992, 993, 994,
                   995, 996, 997, 998, 999, 1000, 1001, 1002, 1003, 1004, 1005,
                   1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015,
                   1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025,
                   1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035,
                   1089]

MISSING_PACKETS = [4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16, 17, 18,
                   19, 20, 22, 23]

print(DATA_PKT1)


def get_data_file(path=SAVED_FILE_PATH) -> str:
    """
    Get the file where the data for the tests should be saved at and return
    it as a string

    Returns (str): string of data saved in the saved data file

    """
    if os.path.isfile(path):
        with open(path, 'r', encoding="utf-8") as _file:
            return _file.read()
    else:
        return "No file yet"


@freezegun.freeze_time(TEST_DATE)
class TestAddDataPacket(unittest.TestCase):
    """
    Test that on start up of the data_class.TimeStreamData that the
    classes add_data_pkt works properly for good data and also data that
    should be ignored, and it will test for a date change.
    """
    def setUp(self) -> None:
        """
        Check that the tearDown method is clearing the saved files that are made,
        initialize the data_class.TimeStreamData class and save to self.
        """
        if get_data_file() != "No file yet":  # make sure not file yet for this testcase
            self.tearDown()
        self.assertEqual(get_data_file(), "No file yet",
                         msg="File is not being deleted between tests correctly")
        with mock.patch("GUI.main_gui.RBOGUI", new_callable=mock.PropertyMock,
                        return_value=True) as mocked_gui:
            self.tsd = data_class.TimeStreamData(mocked_gui)

    def tearDown(self) -> None:
        """
        Delete any saved filed for the simulated test data that
        could have been made from adding a data packet
        """
        if os.path.exists(SAVED_FILE_PATH):
            os.remove(SAVED_FILE_PATH)

    def test_add_data_pkt(self):
        """
        Test that when calling the data_class.TimeStreamData method of
        add_data() that it adds a correct data packet correctly.
        The data packet should be added correct so the method will
        return a 0 code, and the device data will be checked and that
        the data is saved to a file correctly.
        """
        data_dict = json.loads(DATA_PKT1)
        returned_value = self.tsd.add_data(data_dict)
        device_data = \
            self.tsd.positions["position 2"]  # type: GUI.data_class.DeviceData
        self.assertEqual(returned_value, 0,
                         msg="add_data is not returning a zero but an error code")
        self.assertListEqual(device_data.time_series,
                             [dt.datetime(2022, 11, 18, 9, 55, 22)],
                             msg="add_data is not saving a single time_series "
                                 "correctly")
        self.assertListEqual(device_data.av, [-1.0])
        self.assertListEqual(device_data.oryzanol, [-20139.0],
                             msg="add_data is not saving a single oryzanol correctly")
        self.assertEqual(get_data_file(),
                         "time, position, OryConc, AV, CPUTemp, SensorTemp, packet_id\n"
                         "09:55:22, position 2, -20139, -1, 48.31, 0, 1, \n",
                         msg=f"Saved data file is not right for test_add_data_pkt")

    def test_add_2_pkts(self):
        """
        Test that adding 2 packets creates the correct device data
        time_stream and oryzanol attribute lists.  Use the test_add_data_pkt()
        to add the first packet again. Then check the second packet is added
        correctly, and the return code, device_data time_series and oryzanol
        attributes, and the saved file are correct.
        """
        self.test_add_data_pkt()  # add first data packet in other test
        # add second packet
        returned_value = self.tsd.add_data(json.loads(DATA_PKT2))
        device_data = \
            self.tsd.positions["position 2"]  # type: GUI.data_class.DeviceData
        self.assertListEqual(device_data.time_series,
                             [dt.datetime(2022, 11, 18, 9, 55, 22),
                              dt.datetime(2022, 11, 18, 10, 5, 13)],
                             msg="add_data is not saving a second time_series "
                                 "correctly")
        self.assertListEqual(device_data.oryzanol, [-20139.0, -20602.0],
                             msg="add_data is not saving a second oryzanol "
                                 "data packet correctly")
        self.assertEqual(returned_value, 0,
                         msg="add_data is not returning a zero but an error code"
                             "for the second packet")
        self.assertEqual(get_data_file(),
                         "time, position, OryConc, AV, CPUTemp, SensorTemp, packet_id\n"
                         "09:55:22, position 2, -20139, -1, 48.31, 0, 1, \n"
                         "10:05:13, position 2, -20602, -2, 48.31, 41.79, 3, \n",
                         msg=f"Saved data file is not right for test_add_2_pkts")

    def test_make_save_file(self):
        """
        Test that initializing data_class.TimeStreamData (done in setup) will
        create a file with the correct header
        """
        self.assertEqual(get_data_file(), "time, position, OryConc, AV, CPUTemp,"
                                          " SensorTemp, packet_id\n",
                         msg="saved data file not being created correctly"
                             "on startup")

    def test_non_dict_data(self):
        """ Test that if a non-dict is passed to data_class.TimeStreamData
        it just returns a 204 error code"""
        returned_value = self.tsd.add_data("Not a dict")
        self.assertEqual(returned_value, 204,
                         msg="add_data is not returning the correct error code"
                             "for a non-dictionary data type")

    def test_missing_device_key(self):
        """ Test that if the data packet dictionary is missing a "device" or "position"
        key that the add_data method returns the correct 200 error code" """
        returned_value = self.tsd.add_data(json.loads(DATA_PKT_MISSING_DEVICE))
        self.assertEqual(returned_value, 200,
                         msg="add_data is not returning the correct error code"
                             "for a data packet missing a device key")

    def test_add_same_pkt_twice(self):
        """ Test that when a data packet is added twice, the second time
        the packet is rejected and not added """
        self.test_add_data_pkt()
        returned_value = self.tsd.add_data(json.loads(DATA_PKT1))
        device_data = \
            self.tsd.positions["position 2"]  # type: GUI.data_class.DeviceData
        self.assertEqual(returned_value, 222,
                         msg="add_data is not returning a zero but an error code")
        self.assertListEqual(device_data.time_series,
                             [dt.datetime(2022, 11, 18, 9, 55, 22)],
                             msg="add_data is not saving a single time_series "
                                 "correctly")
        self.assertListEqual(device_data.oryzanol, [-20139.0],
                             msg="add_data is not saving a single oryzanol correctly")
        self.assertEqual(get_data_file(), "time, position, OryConc, AV, CPUTemp, SensorTemp, packet_id\n"
                                          "09:55:22, position 2, -20139, -1, 48.31, 0, 1, \n",
                         msg=f"Saved data file is not right for test_add_data_pkt")


@freezegun.freeze_time(TEST_DATE)
class TestLoadData(unittest.TestCase):
    """
    Test that when you start data_class.TimeStreamData with a mocked
    unsorted data file (with a mocked, frozen date), the data class
    will sort and save the file, save the packet ids in the right order
    and can calculate the missing packets that are needed.
    """
    @classmethod
    def setUpClass(cls) -> None:
        """
        Take the template.csv file in the test folder and copy it
        into the data folder for the data_class to use.
        """
        shutil.copyfile(TEMPLATE_FILE, SAVED_FILE_PATH)
        with mock.patch("GUI.main_gui.RBOGUI", new_callable=mock.PropertyMock,
                        return_value=True) as mocked_gui:
            cls.tsd = data_class.TimeStreamData(mocked_gui)

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Delete the mocked data file that should have been sorted
        """
        if os.path.exists(SAVED_FILE_PATH):
            os.remove(SAVED_FILE_PATH)

    def test_load_file(self):
        """
        Test that the TimeStreamData class will read an unsorted
        data file and sort the file and save it in the same place.
        """
        # test if the function is sorting and saving correctly
        self.assertTrue(
            filecmp.cmp(SAVED_FILE_PATH, SORTED_TEMPLATE_FILE,
                        shallow=False),
            msg="Sorted file is not correct after loading and saving")

    def test_add_pos2_av(self):
        """ Test that when reading the saved file data that the acid
        values are loaded in to the data class correctly """
        print(f"av: {self.tsd.positions['position 2'].av}")

    def test_packet_ids(self):
        """
        Test that the packet ids that were loaded when from the saved
        file are correct
        """
        self.assertListEqual(self.tsd.positions['position 2'].packet_ids,
                             CORRECT_PACKET_IDS, msg="packet_ids not correct")

    def test_calc_missing_pkts(self):
        """
        Test that after start up with the mocked data file that
        the time stream data class can calculate the correct
        packet ids that are missing to ask from the sensor
        """
        device_data = self.tsd.positions['position 2']  # type: data_class.DeviceData
        missing_pkts = self.tsd.find_next_missing_pkts(device_data, 24)
        print(missing_pkts)
        self.assertListEqual(missing_pkts, MISSING_PACKETS,
                             msg="Missing packets list wrong")


@freezegun.freeze_time(TEST_DATE)
class TestAddPos1DataPacket(unittest.TestCase):
    def setUp(self) -> None:
        """
        Check that the tearDown method is clearing the saved files that are made,
        initialize the data_class.TimeStreamData class and save to self.
        """
        if get_data_file() != "No file yet":  # make sure not file yet for this testcase
            self.tearDown()
        self.assertEqual(get_data_file(), "No file yet",
                         msg="File is not being deleted between tests correctly")
        with mock.patch("GUI.main_gui.RBOGUI", new_callable=mock.PropertyMock,
                        return_value=True) as mocked_gui:
            self.tsd = data_class.TimeStreamData(mocked_gui)

    def tearDown(self) -> None:
        """
        Delete any saved filed for the simulated test data that
        could have been made from adding a data packet
        """
        if os.path.exists(SAVED_FILE_PATH):
            os.remove(SAVED_FILE_PATH)

    def test_add_av(self):
        print("keys: ", self.tsd.positions.keys())
        data_dict = json.loads(DATA_PKT_POSITION_1)
        returned_value = self.tsd.add_data(data_dict)
        print(returned_value)
        print(self.tsd.positions.keys())
        device_data = \
            self.tsd.positions["position 1"]  # type: GUI.data_class.DeviceData
        # av_data = \
        #     self.tsd.positions["av"]  # type: GUI.data_class.DeviceData
        print(f"device data: {device_data.time_series}")
        print(f"device data: {device_data.oryzanol}")
        # print(f"av data: {av_data}")
        print(get_data_file())
        self.assertEqual(returned_value, 0,
                         msg="add_data is not returning a zero but an error code")
        self.assertListEqual(device_data.time_series,
                             [dt.datetime(2022, 11, 18, 23, 6, 13)],
                             msg="add_data is not saving a single time_series "
                                 "correctly")
        self.assertListEqual(device_data.oryzanol, [-20648.0],
                             msg="add_data is not saving a single oryzanol correctly")
        self.assertListEqual(device_data.av, [10.0],
                             msg="add_data is not saving a single oryzanol correctly")
        self.assertEqual(get_data_file(),
                         "time, position, OryConc, AV, CPUTemp, SensorTemp, packet_id\n"
                         "23:06:13, position 1, -20648, 10, 47.24, 0, 46, \n",
                         msg=f"Saved data file is not right for test_add_av")


@freezegun.freeze_time(TEST_DATE)
class TestChangeDate(unittest.TestCase):
    def setUp(self) -> None:
        """
        Check that the tearDown method is clearing the saved files that are made,
        initialize the data_class.TimeStreamData class and save to self.
        """
        if get_data_file() != "No file yet":  # make sure not file yet for this testcase
            self.tearDown()
        self.assertEqual(get_data_file(), "No file yet",
                         msg="File is not being deleted between tests correctly")
        with mock.patch("GUI.main_gui.RBOGUI", new_callable=mock.PropertyMock,
                        return_value=True) as mocked_gui:
            self.tsd = data_class.TimeStreamData(mocked_gui)

    def tearDown(self) -> None:
        """
        Delete any saved filed for the simulated test data that
        could have been made from adding a data packet
        """
        if os.path.exists(SAVED_FILE_PATH):
            os.remove(SAVED_FILE_PATH)
        if os.path.exists(TOMORROW_FILE_PATH):
            os.remove(TOMORROW_FILE_PATH)

    def test_old_data_pkt_added(self):
        """Test if a packet with an older date is ignored by
        the TimeStreamData class by returning the 201 code"""
        returned_value = self.tsd.add_data(json.loads(DATA_PKT_OLD))
        device_data = \
            self.tsd.positions["position 2"]  # type: GUI.data_class.DeviceData
        self.assertListEqual(device_data.oryzanol, [],
                             msg="add_data is not ignoring an old "
                                 "data packet correctly")
        self.assertEqual(returned_value, 201,
                         msg="add_data is not returning an error code"
                             "for old data")

    def test_new_date(self):
        """ Test that when adding a packet with a date that simulates a new day
        first add DATA_PKT1 (device 2 11-18), """
        # first repeat the adding data packet 1
        data_dict = json.loads(DATA_PKT1)
        returned_value = self.tsd.add_data(data_dict)
        device_data = \
            self.tsd.positions["position 2"]  # type: GUI.data_class.DeviceData
        self.assertEqual(returned_value, 0,
                         msg="add_data is not returning a zero but an error code")
        self.assertListEqual(device_data.time_series,
                             [dt.datetime(2022, 11, 18, 9, 55, 22)],
                             msg="add_data is not saving a single time_series "
                                 "correctly")
        self.assertListEqual(device_data.oryzanol, [-20139.0],
                             msg="add_data is not saving a single oryzanol correctly")
        self.assertEqual(get_data_file(),
                         "time, position, OryConc, AV, CPUTemp, SensorTemp, packet_id\n"
                         "09:55:22, position 2, -20139, -1, 48.31, 0, 1, \n",
                         msg=f"Saved data file is not right for test_add_data_pkt")
        data_dict = json.loads(DATA_PKT_POSITION_1)
        returned_value = self.tsd.add_data(data_dict)
        freeze1 = freezegun.freeze_time(NEXT_DATE)
        freeze1.start()
        returned_value = self.tsd.add_data(json.loads(DATA_PKT_NEW))
        device_data = \
            self.tsd.positions["position 2"]  # type: GUI.data_class.DeviceData

        returned_value = self.tsd.add_data(json.loads(DATA_PKT_POSITION_1_NEW))
        device_data = \
            self.tsd.positions["position 1"]  # type: GUI.data_class.DeviceData
        self.assertEqual(returned_value, 0,
                         msg="add_data is not returning a zero but an error code"
                             "for changing the date forward")
        self.assertListEqual(device_data.oryzanol, [-20111.0],
                             msg="add_data is not saving the oryzanol value for a "
                                 "data packet set for a new day")
        self.assertEqual(get_data_file(TOMORROW_FILE_PATH),
                         "time, position, OryConc, AV, CPUTemp, SensorTemp, packet_id\n"
                         "00:06:13, position 2, -20648, -5, 47.24, 0, 4, \n"
                         "00:07:13, position 1, -20111, 12, 47.24, 0, 4, \n",
                         msg=f"Saved data file is not right for test_add_data_pkt")
        freeze1.stop()


@freezegun.freeze_time(TEST_DATE)
class TestUpdateGraph(unittest.TestCase):
    def tearDown(self) -> None:
        """
        Delete any saved filed for the simulated test data that
        could have been made from adding a data packet
        """
        if os.path.exists(SAVED_FILE_PATH):
            os.remove(SAVED_FILE_PATH)
        if os.path.exists(TOMORROW_FILE_PATH):
            os.remove(TOMORROW_FILE_PATH)

    @mock.patch("GUI.main_gui.RBOGUI")
    def test_update_called(self, mocked_gui):
        self.tsd = data_class.TimeStreamData(mocked_gui)
        data_dict = json.loads(DATA_PKT1)
        returned_value = self.tsd.add_data(data_dict)
        device_data = \
            self.tsd.positions["position 2"]  # type: GUI.data_class.DeviceData
        self.tsd.update_graph("position 2")
        mock_graph = mocked_gui.return_value.master_graph
        pos, device_data = mocked_gui.graphs.update.mock_calls[0].args
        print(f"position: {pos}, data: {device_data}")
        print(f"av data: {device_data.av}")


@freezegun.freeze_time(TEST_DATE)
class TestLoadPreviousData(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """
        Take the template_short.csv file in the test folder and copy it
        into the data folder for the data_class to use.
        """
        shutil.copyfile(TEMPLATE_FILE, SAVED_FILE_PATH)

    def test_load_previous_data(self):
        """ TimeStreamData will attempt to load previous data"""
        with mock.patch("GUI.main_gui.RBOGUI", new_callable=mock.PropertyMock,
                        return_value=True) as mocked_gui:
            self.tsd = data_class.TimeStreamData(mocked_gui)

            self.assertListEqual(self.tsd.positions['position 2'].av, [-1.0, -2.0, -3.0, -4.0, -5.0, -6.0, -7.0])


class TestLoadMixedData(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """
        Take the template_short.csv file in the test folder and copy it
        into the data folder for the data_class to use.
        """
        shutil.copyfile(MISSING_AV_FILE, SAVED_FILE_PATH)

    def test_load_previous_data_w_missing_av(self):
        """ TimeStreamData will attempt to load previous data"""
        with mock.patch("GUI.main_gui.RBOGUI", new_callable=mock.PropertyMock,
                        return_value=True) as mocked_gui:
            self.tsd = data_class.TimeStreamData(mocked_gui)

            # self.assertListEqual(self.tsd.positions['position 2'].av, [-1.0, -2.0, -3.0, -4.0, -5.0, -6.0, -7.0])
            print(f"av: {self.tsd.positions['position 2'].av}")


if __name__ == '__main__':
    unittest.main()

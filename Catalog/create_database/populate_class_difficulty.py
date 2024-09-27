import sqlite3
# db connection created w/in utils
from utils import conn, c, drop_table, drop_view, column_exists

## Make sure these tables are created in the appropriate place
## We can populate them here as examples

################################################################
# Course Difficulty data

difficulty = [
 {
   "class": "AASP 201",
   "PassingStudents": 872,
   "TotalStudents": 976,
   "PassPercentage": 89.34,
   "Difficulty": "Medium"
 },
 {
   "class": "ACCT 220",
   "PassingStudents": 4459,
   "TotalStudents": 5801,
   "PassPercentage": 76.87,
   "Difficulty": "High"
 },
 {
   "class": "ACCT 221",
   "PassingStudents": 3896,
   "TotalStudents": 4522,
   "PassPercentage": 86.16,
   "Difficulty": "Medium"
 },
 {
   "class": "ACCT 301",
   "PassingStudents": 1579,
   "TotalStudents": 1834,
   "PassPercentage": 86.1,
   "Difficulty": "Medium"
 },
 {
   "class": "ACCT 310",
   "PassingStudents": 2683,
   "TotalStudents": 3219,
   "PassPercentage": 83.35,
   "Difficulty": "Medium"
 },
 {
   "class": "ACCT 311",
   "PassingStudents": 1913,
   "TotalStudents": 2169,
   "PassPercentage": 88.2,
   "Difficulty": "Medium"
 },
 {
   "class": "ACCT 320",
   "PassingStudents": 725,
   "TotalStudents": 787,
   "PassPercentage": 92.12,
   "Difficulty": "Low"
 },
 {
   "class": "ACCT 321",
   "PassingStudents": 1333,
   "TotalStudents": 1543,
   "PassPercentage": 86.39,
   "Difficulty": "Medium"
 },
 {
   "class": "ACCT 323",
   "PassingStudents": 1037,
   "TotalStudents": 1223,
   "PassPercentage": 84.79,
   "Difficulty": "Medium"
 },
 {
   "class": "ACCT 326",
   "PassingStudents": 605,
   "TotalStudents": 687,
   "PassPercentage": 88.06,
   "Difficulty": "Medium"
 },
 {
   "class": "ACCT 328",
   "PassingStudents": 29,
   "TotalStudents": 30,
   "PassPercentage": 96.67,
   "Difficulty": "Low"
 },
 {
   "class": "ACCT 350",
   "PassingStudents": 62,
   "TotalStudents": 66,
   "PassPercentage": 93.94,
   "Difficulty": "Low"
 },
 {
   "class": "ACCT 410",
   "PassingStudents": 334,
   "TotalStudents": 373,
   "PassPercentage": 89.54,
   "Difficulty": "Medium"
 },
 {
   "class": "ACCT 411",
   "PassingStudents": 326,
   "TotalStudents": 349,
   "PassPercentage": 93.41,
   "Difficulty": "Low"
 },
 {
   "class": "ACCT 417",
   "PassingStudents": 424,
   "TotalStudents": 464,
   "PassPercentage": 91.38,
   "Difficulty": "Low"
 },
 {
   "class": "ACCT 422",
   "PassingStudents": 408,
   "TotalStudents": 448,
   "PassPercentage": 91.07,
   "Difficulty": "Low"
 },
 {
   "class": "ACCT 424",
   "PassingStudents": 637,
   "TotalStudents": 697,
   "PassPercentage": 91.39,
   "Difficulty": "Low"
 },
 {
   "class": "ACCT 425",
   "PassingStudents": 518,
   "TotalStudents": 547,
   "PassPercentage": 94.7,
   "Difficulty": "Low"
 },
 {
   "class": "ACCT 436",
   "PassingStudents": 422,
   "TotalStudents": 444,
   "PassPercentage": 95.05,
   "Difficulty": "Low"
 },
 {
   "class": "ACCT 438",
   "PassingStudents": 233,
   "TotalStudents": 249,
   "PassPercentage": 93.57,
   "Difficulty": "Low"
 },
 {
   "class": "ACCT 440",
   "PassingStudents": 97,
   "TotalStudents": 105,
   "PassPercentage": 92.38,
   "Difficulty": "Low"
 },
 {
   "class": "ACCT 452",
   "PassingStudents": 9,
   "TotalStudents": 10,
   "PassPercentage": 90,
   "Difficulty": "Low"
 },
 {
   "class": "ACCT 486A",
   "PassingStudents": 5,
   "TotalStudents": 5,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "ACCT 495",
   "PassingStudents": 14,
   "TotalStudents": 15,
   "PassPercentage": 93.33,
   "Difficulty": "Low"
 },
 {
   "class": "ACCT 610",
   "PassingStudents": 52,
   "TotalStudents": 67,
   "PassPercentage": 77.61,
   "Difficulty": "High"
 },
 {
   "class": "ACCT 611",
   "PassingStudents": 19,
   "TotalStudents": 20,
   "PassPercentage": 95,
   "Difficulty": "Low"
 },
 {
   "class": "ACCT 612",
   "PassingStudents": 38,
   "TotalStudents": 39,
   "PassPercentage": 97.44,
   "Difficulty": "Low"
 },
 {
   "class": "ACCT 613",
   "PassingStudents": 42,
   "TotalStudents": 43,
   "PassPercentage": 97.67,
   "Difficulty": "Low"
 },
 {
   "class": "ACCT 625",
   "PassingStudents": 51,
   "TotalStudents": 52,
   "PassPercentage": 98.08,
   "Difficulty": "Low"
 },
 {
   "class": "ACCT 630",
   "PassingStudents": 22,
   "TotalStudents": 22,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "ACCT 640",
   "PassingStudents": 31,
   "TotalStudents": 32,
   "PassPercentage": 96.88,
   "Difficulty": "Low"
 },
 {
   "class": "ACM 620",
   "PassingStudents": 51,
   "TotalStudents": 51,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "AMBA 600",
   "PassingStudents": 11,
   "TotalStudents": 15,
   "PassPercentage": 73.33,
   "Difficulty": "High"
 },
 {
   "class": "AMBA 610",
   "PassingStudents": 29,
   "TotalStudents": 29,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "AMBA 620",
   "PassingStudents": 45,
   "TotalStudents": 47,
   "PassPercentage": 95.74,
   "Difficulty": "Low"
 },
 {
   "class": "AMBA 640",
   "PassingStudents": 139,
   "TotalStudents": 144,
   "PassPercentage": 96.53,
   "Difficulty": "Low"
 },
 {
   "class": "AMBA 650",
   "PassingStudents": 527,
   "TotalStudents": 534,
   "PassPercentage": 98.69,
   "Difficulty": "Low"
 },
 {
   "class": "AMBA 660",
   "PassingStudents": 244,
   "TotalStudents": 251,
   "PassPercentage": 97.21,
   "Difficulty": "Low"
 },
 {
   "class": "AMBA 670",
   "PassingStudents": 56,
   "TotalStudents": 56,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "ANTH 101",
   "PassingStudents": 482,
   "TotalStudents": 535,
   "PassPercentage": 90.09,
   "Difficulty": "Low"
 },
 {
   "class": "ANTH 102",
   "PassingStudents": 594,
   "TotalStudents": 660,
   "PassPercentage": 90,
   "Difficulty": "Low"
 },
 {
   "class": "ANTH 345",
   "PassingStudents": 184,
   "TotalStudents": 193,
   "PassPercentage": 95.34,
   "Difficulty": "Low"
 },
 {
   "class": "ANTH 346",
   "PassingStudents": 155,
   "TotalStudents": 173,
   "PassPercentage": 89.6,
   "Difficulty": "Medium"
 },
 {
   "class": "ANTH 350",
   "PassingStudents": 349,
   "TotalStudents": 378,
   "PassPercentage": 92.33,
   "Difficulty": "Low"
 },
 {
   "class": "ANTH 351",
   "PassingStudents": 220,
   "TotalStudents": 236,
   "PassPercentage": 93.22,
   "Difficulty": "Low"
 },
 {
   "class": "ANTH 417",
   "PassingStudents": 121,
   "TotalStudents": 135,
   "PassPercentage": 89.63,
   "Difficulty": "Medium"
 },
 {
   "class": "APTC 495",
   "PassingStudents": 15,
   "TotalStudents": 16,
   "PassPercentage": 93.75,
   "Difficulty": "Low"
 },
 {
   "class": "ARAB 111",
   "PassingStudents": 132,
   "TotalStudents": 146,
   "PassPercentage": 90.41,
   "Difficulty": "Low"
 },
 {
   "class": "ARAB 112",
   "PassingStudents": 26,
   "TotalStudents": 27,
   "PassPercentage": 96.3,
   "Difficulty": "Low"
 },
 {
   "class": "ARAB 114",
   "PassingStudents": 2,
   "TotalStudents": 2,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "ARAB 333",
   "PassingStudents": 63,
   "TotalStudents": 66,
   "PassPercentage": 95.45,
   "Difficulty": "Low"
 },
 {
   "class": "ARTH 204",
   "PassingStudents": 616,
   "TotalStudents": 677,
   "PassPercentage": 90.99,
   "Difficulty": "Low"
 },
 {
   "class": "ARTH 334",
   "PassingStudents": 3847,
   "TotalStudents": 4284,
   "PassPercentage": 89.8,
   "Difficulty": "Medium"
 },
 {
   "class": "ARTH 372",
   "PassingStudents": 891,
   "TotalStudents": 1150,
   "PassPercentage": 77.48,
   "Difficulty": "High"
 },
 {
   "class": "ARTH 373",
   "PassingStudents": 168,
   "TotalStudents": 218,
   "PassPercentage": 77.06,
   "Difficulty": "High"
 },
 {
   "class": "ARTH 375",
   "PassingStudents": 197,
   "TotalStudents": 218,
   "PassPercentage": 90.37,
   "Difficulty": "Low"
 },
 {
   "class": "ARTH 478",
   "PassingStudents": 228,
   "TotalStudents": 260,
   "PassPercentage": 87.69,
   "Difficulty": "Medium"
 },
 {
   "class": "ARTT 110",
   "PassingStudents": 1546,
   "TotalStudents": 1727,
   "PassPercentage": 89.52,
   "Difficulty": "Medium"
 },
 {
   "class": "ARTT 120",
   "PassingStudents": 188,
   "TotalStudents": 208,
   "PassPercentage": 90.38,
   "Difficulty": "Low"
 },
 {
   "class": "ARTT 152",
   "PassingStudents": 2596,
   "TotalStudents": 2948,
   "PassPercentage": 88.06,
   "Difficulty": "Medium"
 },
 {
   "class": "ARTT 210",
   "PassingStudents": 329,
   "TotalStudents": 363,
   "PassPercentage": 90.63,
   "Difficulty": "Low"
 },
 {
   "class": "ARTT 320",
   "PassingStudents": 195,
   "TotalStudents": 207,
   "PassPercentage": 94.2,
   "Difficulty": "Low"
 },
 {
   "class": "ARTT 428",
   "PassingStudents": 120,
   "TotalStudents": 131,
   "PassPercentage": 91.6,
   "Difficulty": "Low"
 },
 {
   "class": "ASCM 626",
   "PassingStudents": 35,
   "TotalStudents": 37,
   "PassPercentage": 94.59,
   "Difficulty": "Low"
 },
 {
   "class": "ASCM 627",
   "PassingStudents": 17,
   "TotalStudents": 18,
   "PassPercentage": 94.44,
   "Difficulty": "Low"
 },
 {
   "class": "ASCM 628",
   "PassingStudents": 103,
   "TotalStudents": 107,
   "PassPercentage": 96.26,
   "Difficulty": "Low"
 },
 {
   "class": "ASTD 135",
   "PassingStudents": 279,
   "TotalStudents": 314,
   "PassPercentage": 88.85,
   "Difficulty": "Medium"
 },
 {
   "class": "ASTD 155",
   "PassingStudents": 67,
   "TotalStudents": 95,
   "PassPercentage": 70.53,
   "Difficulty": "High"
 },
 {
   "class": "ASTD 284",
   "PassingStudents": 305,
   "TotalStudents": 348,
   "PassPercentage": 87.64,
   "Difficulty": "Medium"
 },
 {
   "class": "ASTD 285",
   "PassingStudents": 228,
   "TotalStudents": 268,
   "PassPercentage": 85.07,
   "Difficulty": "Medium"
 },
 {
   "class": "ASTD 370",
   "PassingStudents": 37,
   "TotalStudents": 39,
   "PassPercentage": 94.87,
   "Difficulty": "Low"
 },
 {
   "class": "ASTD 396",
   "PassingStudents": 7,
   "TotalStudents": 8,
   "PassPercentage": 87.5,
   "Difficulty": "Medium"
 },
 {
   "class": "ASTD 485",
   "PassingStudents": 73,
   "TotalStudents": 79,
   "PassPercentage": 92.41,
   "Difficulty": "Low"
 },
 {
   "class": "ASTR 100",
   "PassingStudents": 720,
   "TotalStudents": 814,
   "PassPercentage": 88.45,
   "Difficulty": "Medium"
 },
 {
   "class": "BEHS 103",
   "PassingStudents": 2709,
   "TotalStudents": 3178,
   "PassPercentage": 85.24,
   "Difficulty": "Medium"
 },
 {
   "class": "BEHS 210",
   "PassingStudents": 895,
   "TotalStudents": 1007,
   "PassPercentage": 88.88,
   "Difficulty": "Medium"
 },
 {
   "class": "BEHS 220",
   "PassingStudents": 1216,
   "TotalStudents": 1345,
   "PassPercentage": 90.41,
   "Difficulty": "Low"
 },
 {
   "class": "BEHS 250",
   "PassingStudents": 336,
   "TotalStudents": 380,
   "PassPercentage": 88.42,
   "Difficulty": "Medium"
 },
 {
   "class": "BEHS 300",
   "PassingStudents": 312,
   "TotalStudents": 330,
   "PassPercentage": 94.55,
   "Difficulty": "Low"
 },
 {
   "class": "BEHS 320",
   "PassingStudents": 1538,
   "TotalStudents": 1619,
   "PassPercentage": 95,
   "Difficulty": "Low"
 },
 {
   "class": "BEHS 343",
   "PassingStudents": 2518,
   "TotalStudents": 2741,
   "PassPercentage": 91.86,
   "Difficulty": "Low"
 },
 {
   "class": "BEHS 364",
   "PassingStudents": 1664,
   "TotalStudents": 1786,
   "PassPercentage": 93.17,
   "Difficulty": "Low"
 },
 {
   "class": "BEHS 380",
   "PassingStudents": 711,
   "TotalStudents": 746,
   "PassPercentage": 95.31,
   "Difficulty": "Low"
 },
 {
   "class": "BEHS 453",
   "PassingStudents": 863,
   "TotalStudents": 912,
   "PassPercentage": 94.63,
   "Difficulty": "Low"
 },
 {
   "class": "BEHS 486B",
   "PassingStudents": 1,
   "TotalStudents": 1,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "BEHS 495",
   "PassingStudents": 288,
   "TotalStudents": 314,
   "PassPercentage": 91.72,
   "Difficulty": "Low"
 },
 {
   "class": "BIFS 614",
   "PassingStudents": 25,
   "TotalStudents": 27,
   "PassPercentage": 92.59,
   "Difficulty": "Low"
 },
 {
   "class": "BIFS 618",
   "PassingStudents": 11,
   "TotalStudents": 12,
   "PassPercentage": 91.67,
   "Difficulty": "Low"
 },
 {
   "class": "BIFS 619",
   "PassingStudents": 15,
   "TotalStudents": 15,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 101",
   "PassingStudents": 3774,
   "TotalStudents": 4309,
   "PassPercentage": 87.58,
   "Difficulty": "Medium"
 },
 {
   "class": "BIOL 102",
   "PassingStudents": 2381,
   "TotalStudents": 2603,
   "PassPercentage": 91.47,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 103",
   "PassingStudents": 9273,
   "TotalStudents": 10623,
   "PassPercentage": 87.29,
   "Difficulty": "Medium"
 },
 {
   "class": "BIOL 105",
   "PassingStudents": 123,
   "TotalStudents": 142,
   "PassPercentage": 86.62,
   "Difficulty": "Medium"
 },
 {
   "class": "BIOL 120",
   "PassingStudents": 16,
   "TotalStudents": 16,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 160",
   "PassingStudents": 3337,
   "TotalStudents": 3724,
   "PassPercentage": 89.61,
   "Difficulty": "Medium"
 },
 {
   "class": "BIOL 161",
   "PassingStudents": 824,
   "TotalStudents": 868,
   "PassPercentage": 94.93,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 164",
   "PassingStudents": 771,
   "TotalStudents": 837,
   "PassPercentage": 92.11,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 181",
   "PassingStudents": 664,
   "TotalStudents": 718,
   "PassPercentage": 92.48,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 182",
   "PassingStudents": 31,
   "TotalStudents": 32,
   "PassPercentage": 96.88,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 201",
   "PassingStudents": 192,
   "TotalStudents": 204,
   "PassPercentage": 94.12,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 202",
   "PassingStudents": 95,
   "TotalStudents": 117,
   "PassPercentage": 81.2,
   "Difficulty": "Medium"
 },
 {
   "class": "BIOL 211",
   "PassingStudents": 76,
   "TotalStudents": 77,
   "PassPercentage": 98.7,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 212",
   "PassingStudents": 42,
   "TotalStudents": 43,
   "PassPercentage": 97.67,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 220",
   "PassingStudents": 115,
   "TotalStudents": 138,
   "PassPercentage": 83.33,
   "Difficulty": "Medium"
 },
 {
   "class": "BIOL 230",
   "PassingStudents": 471,
   "TotalStudents": 516,
   "PassPercentage": 91.28,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 301",
   "PassingStudents": 1320,
   "TotalStudents": 1416,
   "PassPercentage": 93.22,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 302",
   "PassingStudents": 260,
   "TotalStudents": 267,
   "PassPercentage": 97.38,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 304",
   "PassingStudents": 230,
   "TotalStudents": 242,
   "PassPercentage": 95.04,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 307",
   "PassingStudents": 231,
   "TotalStudents": 248,
   "PassPercentage": 93.15,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 318",
   "PassingStudents": 43,
   "TotalStudents": 46,
   "PassPercentage": 93.48,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 320",
   "PassingStudents": 284,
   "TotalStudents": 317,
   "PassPercentage": 89.59,
   "Difficulty": "Medium"
 },
 {
   "class": "BIOL 325",
   "PassingStudents": 208,
   "TotalStudents": 242,
   "PassPercentage": 85.95,
   "Difficulty": "Medium"
 },
 {
   "class": "BIOL 328",
   "PassingStudents": 153,
   "TotalStudents": 169,
   "PassPercentage": 90.53,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 350",
   "PassingStudents": 124,
   "TotalStudents": 130,
   "PassPercentage": 95.38,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 357",
   "PassingStudents": 106,
   "TotalStudents": 134,
   "PassPercentage": 79.1,
   "Difficulty": "High"
 },
 {
   "class": "BIOL 362",
   "PassingStudents": 338,
   "TotalStudents": 371,
   "PassPercentage": 91.11,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 398J",
   "PassingStudents": 96,
   "TotalStudents": 97,
   "PassPercentage": 98.97,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 398L",
   "PassingStudents": 42,
   "TotalStudents": 48,
   "PassPercentage": 87.5,
   "Difficulty": "Medium"
 },
 {
   "class": "BIOL 398N",
   "PassingStudents": 54,
   "TotalStudents": 55,
   "PassPercentage": 98.18,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 398P",
   "PassingStudents": 34,
   "TotalStudents": 37,
   "PassPercentage": 91.89,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 400",
   "PassingStudents": 24,
   "TotalStudents": 24,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 422",
   "PassingStudents": 20,
   "TotalStudents": 24,
   "PassPercentage": 83.33,
   "Difficulty": "Medium"
 },
 {
   "class": "BIOL 486B",
   "PassingStudents": 42,
   "TotalStudents": 43,
   "PassPercentage": 97.67,
   "Difficulty": "Low"
 },
 {
   "class": "BIOL 495",
   "PassingStudents": 319,
   "TotalStudents": 358,
   "PassPercentage": 89.11,
   "Difficulty": "Medium"
 },
 {
   "class": "BIOT 601",
   "PassingStudents": 16,
   "TotalStudents": 16,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "BIOT 630",
   "PassingStudents": 42,
   "TotalStudents": 49,
   "PassPercentage": 85.71,
   "Difficulty": "Medium"
 },
 {
   "class": "BIOT 643",
   "PassingStudents": 837,
   "TotalStudents": 868,
   "PassPercentage": 96.43,
   "Difficulty": "Low"
 },
 {
   "class": "BIOT 645",
   "PassingStudents": 8,
   "TotalStudents": 8,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "BMGT 110",
   "PassingStudents": 6011,
   "TotalStudents": 7061,
   "PassPercentage": 85.13,
   "Difficulty": "Medium"
 },
 {
   "class": "BMGT 121A",
   "PassingStudents": 220,
   "TotalStudents": 261,
   "PassPercentage": 84.29,
   "Difficulty": "Medium"
 },
 {
   "class": "BMGT 121B",
   "PassingStudents": 164,
   "TotalStudents": 187,
   "PassPercentage": 87.7,
   "Difficulty": "Medium"
 },
 {
   "class": "BMGT 160",
   "PassingStudents": 1262,
   "TotalStudents": 1419,
   "PassPercentage": 88.94,
   "Difficulty": "Medium"
 },
 {
   "class": "BMGT 302",
   "PassingStudents": 185,
   "TotalStudents": 205,
   "PassPercentage": 90.24,
   "Difficulty": "Low"
 },
 {
   "class": "BMGT 304",
   "PassingStudents": 573,
   "TotalStudents": 664,
   "PassPercentage": 86.3,
   "Difficulty": "Medium"
 },
 {
   "class": "BMGT 305",
   "PassingStudents": 740,
   "TotalStudents": 827,
   "PassPercentage": 89.48,
   "Difficulty": "Medium"
 },
 {
   "class": "BMGT 317",
   "PassingStudents": 1985,
   "TotalStudents": 2169,
   "PassPercentage": 91.52,
   "Difficulty": "Low"
 },
 {
   "class": "BMGT 330",
   "PassingStudents": 759,
   "TotalStudents": 895,
   "PassPercentage": 84.8,
   "Difficulty": "Medium"
 },
 {
   "class": "BMGT 335",
   "PassingStudents": 772,
   "TotalStudents": 834,
   "PassPercentage": 92.57,
   "Difficulty": "Low"
 },
 {
   "class": "BMGT 339",
   "PassingStudents": 875,
   "TotalStudents": 962,
   "PassPercentage": 90.96,
   "Difficulty": "Low"
 },
 {
   "class": "BMGT 364",
   "PassingStudents": 5534,
   "TotalStudents": 6411,
   "PassPercentage": 86.32,
   "Difficulty": "Medium"
 },
 {
   "class": "BMGT 365",
   "PassingStudents": 3862,
   "TotalStudents": 4168,
   "PassPercentage": 92.66,
   "Difficulty": "Low"
 },
 {
   "class": "BMGT 372",
   "PassingStudents": 38,
   "TotalStudents": 43,
   "PassPercentage": 88.37,
   "Difficulty": "Medium"
 },
 {
   "class": "BMGT 380",
   "PassingStudents": 3150,
   "TotalStudents": 3415,
   "PassPercentage": 92.24,
   "Difficulty": "Low"
 },
 {
   "class": "BMGT 381",
   "PassingStudents": 75,
   "TotalStudents": 81,
   "PassPercentage": 92.59,
   "Difficulty": "Low"
 },
 {
   "class": "BMGT 392",
   "PassingStudents": 126,
   "TotalStudents": 141,
   "PassPercentage": 89.36,
   "Difficulty": "Medium"
 },
 {
   "class": "BMGT 411",
   "PassingStudents": 108,
   "TotalStudents": 118,
   "PassPercentage": 91.53,
   "Difficulty": "Low"
 },
 {
   "class": "BMGT 437",
   "PassingStudents": 12,
   "TotalStudents": 14,
   "PassPercentage": 85.71,
   "Difficulty": "Medium"
 },
 {
   "class": "BMGT 456",
   "PassingStudents": 19,
   "TotalStudents": 19,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "BMGT 464",
   "PassingStudents": 665,
   "TotalStudents": 712,
   "PassPercentage": 93.4,
   "Difficulty": "Low"
 },
 {
   "class": "BMGT 465",
   "PassingStudents": 112,
   "TotalStudents": 116,
   "PassPercentage": 96.55,
   "Difficulty": "Low"
 },
 {
   "class": "BMGT 466",
   "PassingStudents": 46,
   "TotalStudents": 49,
   "PassPercentage": 93.88,
   "Difficulty": "Low"
 },
 {
   "class": "BMGT 482",
   "PassingStudents": 13,
   "TotalStudents": 13,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "BMGT 484",
   "PassingStudents": 474,
   "TotalStudents": 480,
   "PassPercentage": 98.75,
   "Difficulty": "Low"
 },
 {
   "class": "BMGT 485",
   "PassingStudents": 720,
   "TotalStudents": 756,
   "PassPercentage": 95.24,
   "Difficulty": "Low"
 },
 {
   "class": "BMGT 486B",
   "PassingStudents": 11,
   "TotalStudents": 11,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "BMGT 487",
   "PassingStudents": 704,
   "TotalStudents": 808,
   "PassPercentage": 87.13,
   "Difficulty": "Medium"
 },
 {
   "class": "BMGT 488",
   "PassingStudents": 261,
   "TotalStudents": 272,
   "PassPercentage": 95.96,
   "Difficulty": "Low"
 },
 {
   "class": "BMGT 495",
   "PassingStudents": 2572,
   "TotalStudents": 2776,
   "PassPercentage": 92.65,
   "Difficulty": "Low"
 },
 {
   "class": "BMGT 496",
   "PassingStudents": 4848,
   "TotalStudents": 5243,
   "PassPercentage": 92.47,
   "Difficulty": "Low"
 },
 {
   "class": "BSBD 640",
   "PassingStudents": 197,
   "TotalStudents": 210,
   "PassPercentage": 93.81,
   "Difficulty": "Low"
 },
 {
   "class": "BTMN 636",
   "PassingStudents": 23,
   "TotalStudents": 23,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "CAPL 101",
   "PassingStudents": 179,
   "TotalStudents": 187,
   "PassPercentage": 95.72,
   "Difficulty": "Low"
 },
 {
   "class": "CAPL 198A",
   "PassingStudents": 274,
   "TotalStudents": 281,
   "PassPercentage": 97.51,
   "Difficulty": "Low"
 },
 {
   "class": "CAPL 198B",
   "PassingStudents": 8,
   "TotalStudents": 8,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "CAPL 398A",
   "PassingStudents": 1255,
   "TotalStudents": 1307,
   "PassPercentage": 96.02,
   "Difficulty": "Low"
 },
 {
   "class": "CAPL 495",
   "PassingStudents": 431,
   "TotalStudents": 437,
   "PassPercentage": 98.63,
   "Difficulty": "Low"
 },
 {
   "class": "CCJS 100",
   "PassingStudents": 2026,
   "TotalStudents": 2338,
   "PassPercentage": 86.66,
   "Difficulty": "Medium"
 },
 {
   "class": "CCJS 101",
   "PassingStudents": 444,
   "TotalStudents": 520,
   "PassPercentage": 85.38,
   "Difficulty": "Medium"
 },
 {
   "class": "CCJS 105",
   "PassingStudents": 687,
   "TotalStudents": 764,
   "PassPercentage": 89.92,
   "Difficulty": "Medium"
 },
 {
   "class": "CCJS 230",
   "PassingStudents": 679,
   "TotalStudents": 757,
   "PassPercentage": 89.7,
   "Difficulty": "Medium"
 },
 {
   "class": "CCJS 234",
   "PassingStudents": 210,
   "TotalStudents": 243,
   "PassPercentage": 86.42,
   "Difficulty": "Medium"
 },
 {
   "class": "CCJS 301",
   "PassingStudents": 256,
   "TotalStudents": 283,
   "PassPercentage": 90.46,
   "Difficulty": "Low"
 },
 {
   "class": "CCJS 302",
   "PassingStudents": 124,
   "TotalStudents": 131,
   "PassPercentage": 94.66,
   "Difficulty": "Low"
 },
 {
   "class": "CCJS 311",
   "PassingStudents": 119,
   "TotalStudents": 128,
   "PassPercentage": 92.97,
   "Difficulty": "Low"
 },
 {
   "class": "CCJS 321",
   "PassingStudents": 1413,
   "TotalStudents": 1550,
   "PassPercentage": 91.16,
   "Difficulty": "Low"
 },
 {
   "class": "CCJS 340",
   "PassingStudents": 744,
   "TotalStudents": 835,
   "PassPercentage": 89.1,
   "Difficulty": "Medium"
 },
 {
   "class": "CCJS 341",
   "PassingStudents": 592,
   "TotalStudents": 631,
   "PassPercentage": 93.82,
   "Difficulty": "Low"
 },
 {
   "class": "CCJS 342",
   "PassingStudents": 393,
   "TotalStudents": 429,
   "PassPercentage": 91.61,
   "Difficulty": "Low"
 },
 {
   "class": "CCJS 345",
   "PassingStudents": 693,
   "TotalStudents": 743,
   "PassPercentage": 93.27,
   "Difficulty": "Low"
 },
 {
   "class": "CCJS 350",
   "PassingStudents": 398,
   "TotalStudents": 411,
   "PassPercentage": 96.84,
   "Difficulty": "Low"
 },
 {
   "class": "CCJS 352",
   "PassingStudents": 497,
   "TotalStudents": 520,
   "PassPercentage": 95.58,
   "Difficulty": "Low"
 },
 {
   "class": "CCJS 360",
   "PassingStudents": 401,
   "TotalStudents": 436,
   "PassPercentage": 91.97,
   "Difficulty": "Low"
 },
 {
   "class": "CCJS 380",
   "PassingStudents": 654,
   "TotalStudents": 675,
   "PassPercentage": 96.89,
   "Difficulty": "Low"
 },
 {
   "class": "CCJS 390",
   "PassingStudents": 311,
   "TotalStudents": 340,
   "PassPercentage": 91.47,
   "Difficulty": "Low"
 },
 {
   "class": "CCJS 416",
   "PassingStudents": 10,
   "TotalStudents": 10,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "CCJS 420",
   "PassingStudents": 185,
   "TotalStudents": 201,
   "PassPercentage": 92.04,
   "Difficulty": "Low"
 },
 {
   "class": "CCJS 421",
   "PassingStudents": 97,
   "TotalStudents": 101,
   "PassPercentage": 96.04,
   "Difficulty": "Low"
 },
 {
   "class": "CCJS 440",
   "PassingStudents": 77,
   "TotalStudents": 86,
   "PassPercentage": 89.53,
   "Difficulty": "Medium"
 },
 {
   "class": "CCJS 441",
   "PassingStudents": 72,
   "TotalStudents": 76,
   "PassPercentage": 94.74,
   "Difficulty": "Low"
 },
 {
   "class": "CCJS 461",
   "PassingStudents": 317,
   "TotalStudents": 329,
   "PassPercentage": 96.35,
   "Difficulty": "Low"
 },
 {
   "class": "CCJS 495",
   "PassingStudents": 587,
   "TotalStudents": 609,
   "PassPercentage": 96.39,
   "Difficulty": "Low"
 },
 {
   "class": "CCJS 497",
   "PassingStudents": 594,
   "TotalStudents": 618,
   "PassPercentage": 96.12,
   "Difficulty": "Low"
 },
 {
   "class": "CCPA 830A",
   "PassingStudents": 7,
   "TotalStudents": 7,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "CCPA 830B",
   "PassingStudents": 3,
   "TotalStudents": 3,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "CCPA 890",
   "PassingStudents": 1,
   "TotalStudents": 1,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "CHEM 103",
   "PassingStudents": 185,
   "TotalStudents": 223,
   "PassPercentage": 82.96,
   "Difficulty": "Medium"
 },
 {
   "class": "CHEM 113",
   "PassingStudents": 125,
   "TotalStudents": 134,
   "PassPercentage": 93.28,
   "Difficulty": "Low"
 },
 {
   "class": "CHEM 121",
   "PassingStudents": 202,
   "TotalStudents": 220,
   "PassPercentage": 91.82,
   "Difficulty": "Low"
 },
 {
   "class": "CHEM 297",
   "PassingStudents": 165,
   "TotalStudents": 175,
   "PassPercentage": 94.29,
   "Difficulty": "Low"
 },
 {
   "class": "CHIN 111",
   "PassingStudents": 102,
   "TotalStudents": 117,
   "PassPercentage": 87.18,
   "Difficulty": "Medium"
 },
 {
   "class": "CHIN 112",
   "PassingStudents": 25,
   "TotalStudents": 30,
   "PassPercentage": 83.33,
   "Difficulty": "Medium"
 },
 {
   "class": "CHIN 114",
   "PassingStudents": 19,
   "TotalStudents": 19,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "CJMS 600",
   "PassingStudents": 60,
   "TotalStudents": 65,
   "PassPercentage": 92.31,
   "Difficulty": "Low"
 },
 {
   "class": "CJMS 650",
   "PassingStudents": 26,
   "TotalStudents": 27,
   "PassPercentage": 96.3,
   "Difficulty": "Low"
 },
 {
   "class": "CMIS 102",
   "PassingStudents": 4528,
   "TotalStudents": 5320,
   "PassPercentage": 85.11,
   "Difficulty": "Medium"
 },
 {
   "class": "CMIS 111",
   "PassingStudents": 2029,
   "TotalStudents": 2212,
   "PassPercentage": 91.73,
   "Difficulty": "Low"
 },
 {
   "class": "CMIS 115",
   "PassingStudents": 30,
   "TotalStudents": 37,
   "PassPercentage": 81.08,
   "Difficulty": "Medium"
 },
 {
   "class": "CMIS 125",
   "PassingStudents": 46,
   "TotalStudents": 52,
   "PassPercentage": 88.46,
   "Difficulty": "Medium"
 },
 {
   "class": "CMIS 141",
   "PassingStudents": 2326,
   "TotalStudents": 2674,
   "PassPercentage": 86.99,
   "Difficulty": "Medium"
 },
 {
   "class": "CMIS 170",
   "PassingStudents": 142,
   "TotalStudents": 155,
   "PassPercentage": 91.61,
   "Difficulty": "Low"
 },
 {
   "class": "CMIS 225",
   "PassingStudents": 41,
   "TotalStudents": 45,
   "PassPercentage": 91.11,
   "Difficulty": "Low"
 },
 {
   "class": "CMIS 242",
   "PassingStudents": 1763,
   "TotalStudents": 1994,
   "PassPercentage": 88.42,
   "Difficulty": "Medium"
 },
 {
   "class": "CMIS 310",
   "PassingStudents": 718,
   "TotalStudents": 764,
   "PassPercentage": 93.98,
   "Difficulty": "Low"
 },
 {
   "class": "CMIS 315",
   "PassingStudents": 81,
   "TotalStudents": 88,
   "PassPercentage": 92.05,
   "Difficulty": "Low"
 },
 {
   "class": "CMIS 320",
   "PassingStudents": 325,
   "TotalStudents": 371,
   "PassPercentage": 87.6,
   "Difficulty": "Medium"
 },
 {
   "class": "CMIS 325",
   "PassingStudents": 137,
   "TotalStudents": 146,
   "PassPercentage": 93.84,
   "Difficulty": "Low"
 },
 {
   "class": "CMIS 330",
   "PassingStudents": 342,
   "TotalStudents": 397,
   "PassPercentage": 86.15,
   "Difficulty": "Medium"
 },
 {
   "class": "CMIS 420",
   "PassingStudents": 24,
   "TotalStudents": 29,
   "PassPercentage": 82.76,
   "Difficulty": "Medium"
 },
 {
   "class": "CMIS 430",
   "PassingStudents": 10,
   "TotalStudents": 12,
   "PassPercentage": 83.33,
   "Difficulty": "Medium"
 },
 {
   "class": "CMIS 435",
   "PassingStudents": 19,
   "TotalStudents": 21,
   "PassPercentage": 90.48,
   "Difficulty": "Low"
 },
 {
   "class": "CMIS 440",
   "PassingStudents": 91,
   "TotalStudents": 115,
   "PassPercentage": 79.13,
   "Difficulty": "High"
 },
 {
   "class": "CMIS 455",
   "PassingStudents": 10,
   "TotalStudents": 10,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "CMIS 460",
   "PassingStudents": 59,
   "TotalStudents": 62,
   "PassPercentage": 95.16,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 202",
   "PassingStudents": 51,
   "TotalStudents": 58,
   "PassPercentage": 87.93,
   "Difficulty": "Medium"
 },
 {
   "class": "CMIT 265",
   "PassingStudents": 2433,
   "TotalStudents": 2620,
   "PassPercentage": 92.86,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 320",
   "PassingStudents": 52,
   "TotalStudents": 56,
   "PassPercentage": 92.86,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 321",
   "PassingStudents": 89,
   "TotalStudents": 93,
   "PassPercentage": 95.7,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 326",
   "PassingStudents": 2428,
   "TotalStudents": 2659,
   "PassPercentage": 91.31,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 336",
   "PassingStudents": 605,
   "TotalStudents": 617,
   "PassPercentage": 98.06,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 364",
   "PassingStudents": 28,
   "TotalStudents": 30,
   "PassPercentage": 93.33,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 369",
   "PassingStudents": 495,
   "TotalStudents": 561,
   "PassPercentage": 88.24,
   "Difficulty": "Medium"
 },
 {
   "class": "CMIT 370",
   "PassingStudents": 96,
   "TotalStudents": 103,
   "PassPercentage": 93.2,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 371",
   "PassingStudents": 57,
   "TotalStudents": 60,
   "PassPercentage": 95,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 373",
   "PassingStudents": 58,
   "TotalStudents": 58,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 380",
   "PassingStudents": 1647,
   "TotalStudents": 1718,
   "PassPercentage": 95.87,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 382",
   "PassingStudents": 621,
   "TotalStudents": 648,
   "PassPercentage": 95.83,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 386",
   "PassingStudents": 872,
   "TotalStudents": 949,
   "PassPercentage": 91.89,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 388",
   "PassingStudents": 327,
   "TotalStudents": 339,
   "PassPercentage": 96.46,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 391",
   "PassingStudents": 25,
   "TotalStudents": 29,
   "PassPercentage": 86.21,
   "Difficulty": "Medium"
 },
 {
   "class": "CMIT 420",
   "PassingStudents": 195,
   "TotalStudents": 200,
   "PassPercentage": 97.5,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 421",
   "PassingStudents": 1319,
   "TotalStudents": 1378,
   "PassPercentage": 95.72,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 422",
   "PassingStudents": 70,
   "TotalStudents": 71,
   "PassPercentage": 98.59,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 424",
   "PassingStudents": 133,
   "TotalStudents": 141,
   "PassPercentage": 94.33,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 426",
   "PassingStudents": 202,
   "TotalStudents": 204,
   "PassPercentage": 99.02,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 440",
   "PassingStudents": 76,
   "TotalStudents": 77,
   "PassPercentage": 98.7,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 451",
   "PassingStudents": 200,
   "TotalStudents": 215,
   "PassPercentage": 93.02,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 452",
   "PassingStudents": 120,
   "TotalStudents": 127,
   "PassPercentage": 94.49,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 455",
   "PassingStudents": 376,
   "TotalStudents": 389,
   "PassPercentage": 96.66,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 456",
   "PassingStudents": 77,
   "TotalStudents": 79,
   "PassPercentage": 97.47,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 460",
   "PassingStudents": 324,
   "TotalStudents": 349,
   "PassPercentage": 92.84,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 486A",
   "PassingStudents": 9,
   "TotalStudents": 9,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 486B",
   "PassingStudents": 9,
   "TotalStudents": 9,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "CMIT 495",
   "PassingStudents": 3664,
   "TotalStudents": 3748,
   "PassPercentage": 97.76,
   "Difficulty": "Low"
 },
 {
   "class": "CMSC 100",
   "PassingStudents": 474,
   "TotalStudents": 525,
   "PassPercentage": 90.29,
   "Difficulty": "Low"
 },
 {
   "class": "CMSC 105",
   "PassingStudents": 1406,
   "TotalStudents": 1649,
   "PassPercentage": 85.26,
   "Difficulty": "Medium"
 },
 {
   "class": "CMSC 115",
   "PassingStudents": 1189,
   "TotalStudents": 1383,
   "PassPercentage": 85.97,
   "Difficulty": "Medium"
 },
 {
   "class": "CMSC 150",
   "PassingStudents": 1742,
   "TotalStudents": 1832,
   "PassPercentage": 95.09,
   "Difficulty": "Low"
 },
 {
   "class": "CMSC 215",
   "PassingStudents": 1012,
   "TotalStudents": 1154,
   "PassPercentage": 87.69,
   "Difficulty": "Medium"
 },
 {
   "class": "CMSC 307",
   "PassingStudents": 466,
   "TotalStudents": 478,
   "PassPercentage": 97.49,
   "Difficulty": "Low"
 },
 {
   "class": "CMSC 310",
   "PassingStudents": 319,
   "TotalStudents": 329,
   "PassPercentage": 96.96,
   "Difficulty": "Low"
 },
 {
   "class": "CMSC 315",
   "PassingStudents": 572,
   "TotalStudents": 677,
   "PassPercentage": 84.49,
   "Difficulty": "Medium"
 },
 {
   "class": "CMSC 320",
   "PassingStudents": 238,
   "TotalStudents": 257,
   "PassPercentage": 92.61,
   "Difficulty": "Low"
 },
 {
   "class": "CMSC 325",
   "PassingStudents": 295,
   "TotalStudents": 322,
   "PassPercentage": 91.61,
   "Difficulty": "Low"
 },
 {
   "class": "CMSC 330",
   "PassingStudents": 1442,
   "TotalStudents": 1690,
   "PassPercentage": 85.33,
   "Difficulty": "Medium"
 },
 {
   "class": "CMSC 335",
   "PassingStudents": 933,
   "TotalStudents": 1083,
   "PassPercentage": 86.15,
   "Difficulty": "Medium"
 },
 {
   "class": "CMSC 345",
   "PassingStudents": 395,
   "TotalStudents": 435,
   "PassPercentage": 90.8,
   "Difficulty": "Low"
 },
 {
   "class": "CMSC 350",
   "PassingStudents": 1120,
   "TotalStudents": 1290,
   "PassPercentage": 86.82,
   "Difficulty": "Medium"
 },
 {
   "class": "CMSC 405",
   "PassingStudents": 630,
   "TotalStudents": 695,
   "PassPercentage": 90.65,
   "Difficulty": "Low"
 },
 {
   "class": "CMSC 412",
   "PassingStudents": 427,
   "TotalStudents": 486,
   "PassPercentage": 87.86,
   "Difficulty": "Medium"
 },
 {
   "class": "CMSC 420",
   "PassingStudents": 7,
   "TotalStudents": 7,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "CMSC 427",
   "PassingStudents": 45,
   "TotalStudents": 51,
   "PassPercentage": 88.24,
   "Difficulty": "Medium"
 },
 {
   "class": "CMSC 430",
   "PassingStudents": 844,
   "TotalStudents": 916,
   "PassPercentage": 92.14,
   "Difficulty": "Low"
 },
 {
   "class": "CMSC 440",
   "PassingStudents": 13,
   "TotalStudents": 14,
   "PassPercentage": 92.86,
   "Difficulty": "Low"
 },
 {
   "class": "CMSC 451",
   "PassingStudents": 719,
   "TotalStudents": 807,
   "PassPercentage": 89.1,
   "Difficulty": "Medium"
 },
 {
   "class": "CMSC 465",
   "PassingStudents": 38,
   "TotalStudents": 40,
   "PassPercentage": 95,
   "Difficulty": "Low"
 },
 {
   "class": "CMSC 495",
   "PassingStudents": 1376,
   "TotalStudents": 1405,
   "PassPercentage": 97.94,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 100B",
   "PassingStudents": 289,
   "TotalStudents": 306,
   "PassPercentage": 94.44,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 100D",
   "PassingStudents": 214,
   "TotalStudents": 223,
   "PassPercentage": 95.96,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 100F",
   "PassingStudents": 166,
   "TotalStudents": 174,
   "PassPercentage": 95.4,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 100G",
   "PassingStudents": 267,
   "TotalStudents": 281,
   "PassPercentage": 95.02,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 290",
   "PassingStudents": 672,
   "TotalStudents": 714,
   "PassPercentage": 94.12,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 295",
   "PassingStudents": 621,
   "TotalStudents": 662,
   "PassPercentage": 93.81,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 301",
   "PassingStudents": 3127,
   "TotalStudents": 3484,
   "PassPercentage": 89.75,
   "Difficulty": "Medium"
 },
 {
   "class": "CMST 303",
   "PassingStudents": 271,
   "TotalStudents": 291,
   "PassPercentage": 93.13,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 308",
   "PassingStudents": 429,
   "TotalStudents": 476,
   "PassPercentage": 90.13,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 310",
   "PassingStudents": 367,
   "TotalStudents": 377,
   "PassPercentage": 97.35,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 311",
   "PassingStudents": 147,
   "TotalStudents": 148,
   "PassPercentage": 99.32,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 315",
   "PassingStudents": 282,
   "TotalStudents": 330,
   "PassPercentage": 85.45,
   "Difficulty": "Medium"
 },
 {
   "class": "CMST 320",
   "PassingStudents": 404,
   "TotalStudents": 419,
   "PassPercentage": 96.42,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 325",
   "PassingStudents": 763,
   "TotalStudents": 775,
   "PassPercentage": 98.45,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 330",
   "PassingStudents": 64,
   "TotalStudents": 70,
   "PassPercentage": 91.43,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 331",
   "PassingStudents": 49,
   "TotalStudents": 55,
   "PassPercentage": 89.09,
   "Difficulty": "Medium"
 },
 {
   "class": "CMST 341",
   "PassingStudents": 165,
   "TotalStudents": 171,
   "PassPercentage": 96.49,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 351",
   "PassingStudents": 86,
   "TotalStudents": 93,
   "PassPercentage": 92.47,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 355",
   "PassingStudents": 32,
   "TotalStudents": 32,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 385",
   "PassingStudents": 305,
   "TotalStudents": 346,
   "PassPercentage": 88.15,
   "Difficulty": "Medium"
 },
 {
   "class": "CMST 386",
   "PassingStudents": 158,
   "TotalStudents": 166,
   "PassPercentage": 95.18,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 388",
   "PassingStudents": 128,
   "TotalStudents": 131,
   "PassPercentage": 97.71,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 390",
   "PassingStudents": 57,
   "TotalStudents": 61,
   "PassPercentage": 93.44,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 425",
   "PassingStudents": 121,
   "TotalStudents": 123,
   "PassPercentage": 98.37,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 450",
   "PassingStudents": 10,
   "TotalStudents": 10,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 488",
   "PassingStudents": 43,
   "TotalStudents": 44,
   "PassPercentage": 97.73,
   "Difficulty": "Low"
 },
 {
   "class": "CMST 495",
   "PassingStudents": 221,
   "TotalStudents": 229,
   "PassPercentage": 96.51,
   "Difficulty": "Low"
 },
 {
   "class": "COMM 200",
   "PassingStudents": 10,
   "TotalStudents": 12,
   "PassPercentage": 83.33,
   "Difficulty": "Medium"
 },
 {
   "class": "COMM 202",
   "PassingStudents": 805,
   "TotalStudents": 899,
   "PassPercentage": 89.54,
   "Difficulty": "Medium"
 },
 {
   "class": "COMM 207",
   "PassingStudents": 708,
   "TotalStudents": 804,
   "PassPercentage": 88.06,
   "Difficulty": "Medium"
 },
 {
   "class": "COMM 300",
   "PassingStudents": 1314,
   "TotalStudents": 1475,
   "PassPercentage": 89.08,
   "Difficulty": "Medium"
 },
 {
   "class": "COMM 302",
   "PassingStudents": 362,
   "TotalStudents": 416,
   "PassPercentage": 87.02,
   "Difficulty": "Medium"
 },
 {
   "class": "COMM 380",
   "PassingStudents": 19,
   "TotalStudents": 19,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "COMM 390",
   "PassingStudents": 773,
   "TotalStudents": 833,
   "PassPercentage": 92.8,
   "Difficulty": "Low"
 },
 {
   "class": "COMM 400",
   "PassingStudents": 285,
   "TotalStudents": 311,
   "PassPercentage": 91.64,
   "Difficulty": "Low"
 },
 {
   "class": "COMM 480",
   "PassingStudents": 66,
   "TotalStudents": 74,
   "PassPercentage": 89.19,
   "Difficulty": "Medium"
 },
 {
   "class": "COMM 486A",
   "PassingStudents": 1,
   "TotalStudents": 1,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "COMM 492",
   "PassingStudents": 147,
   "TotalStudents": 157,
   "PassPercentage": 93.63,
   "Difficulty": "Low"
 },
 {
   "class": "COMM 493",
   "PassingStudents": 0,
   "TotalStudents": 1,
   "PassPercentage": 0,
   "Difficulty": "High"
 },
 {
   "class": "COMM 495",
   "PassingStudents": 182,
   "TotalStudents": 199,
   "PassPercentage": 91.46,
   "Difficulty": "Low"
 },
 {
   "class": "COMM 600",
   "PassingStudents": 97,
   "TotalStudents": 110,
   "PassPercentage": 88.18,
   "Difficulty": "Medium"
 },
 {
   "class": "CSEC 610",
   "PassingStudents": 37,
   "TotalStudents": 39,
   "PassPercentage": 94.87,
   "Difficulty": "Low"
 },
 {
   "class": "CSEC 620",
   "PassingStudents": 1281,
   "TotalStudents": 1316,
   "PassPercentage": 97.34,
   "Difficulty": "Low"
 },
 {
   "class": "CSEC 635",
   "PassingStudents": 42,
   "TotalStudents": 43,
   "PassPercentage": 97.67,
   "Difficulty": "Low"
 },
 {
   "class": "CSEC 640",
   "PassingStudents": 93,
   "TotalStudents": 94,
   "PassPercentage": 98.94,
   "Difficulty": "Low"
 },
 {
   "class": "CSEC 645",
   "PassingStudents": 79,
   "TotalStudents": 79,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "CSEC 650",
   "PassingStudents": 24,
   "TotalStudents": 24,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "CSEC 655",
   "PassingStudents": 25,
   "TotalStudents": 25,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "CSEC 670",
   "PassingStudents": 824,
   "TotalStudents": 825,
   "PassPercentage": 99.88,
   "Difficulty": "Low"
 },
 {
   "class": "CSIA 300",
   "PassingStudents": 1890,
   "TotalStudents": 2039,
   "PassPercentage": 92.69,
   "Difficulty": "Low"
 },
 {
   "class": "CSIA 310",
   "PassingStudents": 783,
   "TotalStudents": 851,
   "PassPercentage": 92.01,
   "Difficulty": "Low"
 },
 {
   "class": "CSIA 350",
   "PassingStudents": 664,
   "TotalStudents": 697,
   "PassPercentage": 95.27,
   "Difficulty": "Low"
 },
 {
   "class": "CSIA 360",
   "PassingStudents": 559,
   "TotalStudents": 582,
   "PassPercentage": 96.05,
   "Difficulty": "Low"
 },
 {
   "class": "CSIA 413",
   "PassingStudents": 516,
   "TotalStudents": 553,
   "PassPercentage": 93.31,
   "Difficulty": "Low"
 },
 {
   "class": "CSIA 459",
   "PassingStudents": 472,
   "TotalStudents": 491,
   "PassPercentage": 96.13,
   "Difficulty": "Low"
 },
 {
   "class": "CSIA 485",
   "PassingStudents": 491,
   "TotalStudents": 513,
   "PassPercentage": 95.71,
   "Difficulty": "Low"
 },
 {
   "class": "CSIA 486A",
   "PassingStudents": 1,
   "TotalStudents": 1,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "CST 640",
   "PassingStudents": 33,
   "TotalStudents": 33,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "DATA 200",
   "PassingStudents": 324,
   "TotalStudents": 391,
   "PassPercentage": 82.86,
   "Difficulty": "Medium"
 },
 {
   "class": "DATA 220",
   "PassingStudents": 26,
   "TotalStudents": 28,
   "PassPercentage": 92.86,
   "Difficulty": "Low"
 },
 {
   "class": "DATA 230",
   "PassingStudents": 65,
   "TotalStudents": 67,
   "PassPercentage": 97.01,
   "Difficulty": "Low"
 },
 {
   "class": "DATA 300",
   "PassingStudents": 195,
   "TotalStudents": 216,
   "PassPercentage": 90.28,
   "Difficulty": "Low"
 },
 {
   "class": "DATA 320",
   "PassingStudents": 199,
   "TotalStudents": 217,
   "PassPercentage": 91.71,
   "Difficulty": "Low"
 },
 {
   "class": "DATA 430",
   "PassingStudents": 33,
   "TotalStudents": 41,
   "PassPercentage": 80.49,
   "Difficulty": "Medium"
 },
 {
   "class": "DATA 445",
   "PassingStudents": 165,
   "TotalStudents": 166,
   "PassPercentage": 99.4,
   "Difficulty": "Low"
 },
 {
   "class": "DATA 450",
   "PassingStudents": 59,
   "TotalStudents": 64,
   "PassPercentage": 92.19,
   "Difficulty": "Low"
 },
 {
   "class": "DATA 460",
   "PassingStudents": 28,
   "TotalStudents": 28,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "DBST 665",
   "PassingStudents": 12,
   "TotalStudents": 12,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "DEPM 622",
   "PassingStudents": 7,
   "TotalStudents": 10,
   "PassPercentage": 70,
   "Difficulty": "High"
 },
 {
   "class": "DETT 607",
   "PassingStudents": 21,
   "TotalStudents": 24,
   "PassPercentage": 87.5,
   "Difficulty": "Medium"
 },
 {
   "class": "DETT 621",
   "PassingStudents": 37,
   "TotalStudents": 38,
   "PassPercentage": 97.37,
   "Difficulty": "Low"
 },
 {
   "class": "DFC 620",
   "PassingStudents": 106,
   "TotalStudents": 109,
   "PassPercentage": 97.25,
   "Difficulty": "Low"
 },
 {
   "class": "DFC 630",
   "PassingStudents": 4,
   "TotalStudents": 4,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "DFC 640",
   "PassingStudents": 1,
   "TotalStudents": 1,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "DFCS 605",
   "PassingStudents": 1,
   "TotalStudents": 1,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "DMBA 610",
   "PassingStudents": 226,
   "TotalStudents": 232,
   "PassPercentage": 97.41,
   "Difficulty": "Low"
 },
 {
   "class": "DMBA 620",
   "PassingStudents": 102,
   "TotalStudents": 114,
   "PassPercentage": 89.47,
   "Difficulty": "Medium"
 },
 {
   "class": "DMBA 630",
   "PassingStudents": 104,
   "TotalStudents": 105,
   "PassPercentage": 99.05,
   "Difficulty": "Low"
 },
 {
   "class": "DMCC 800",
   "PassingStudents": 12,
   "TotalStudents": 12,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "DMCC 821",
   "PassingStudents": 3,
   "TotalStudents": 3,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "ECON 103",
   "PassingStudents": 2461,
   "TotalStudents": 2601,
   "PassPercentage": 94.62,
   "Difficulty": "Low"
 },
 {
   "class": "ECON 201",
   "PassingStudents": 6284,
   "TotalStudents": 7155,
   "PassPercentage": 87.83,
   "Difficulty": "Medium"
 },
 {
   "class": "ECON 203",
   "PassingStudents": 4786,
   "TotalStudents": 5246,
   "PassPercentage": 91.23,
   "Difficulty": "Low"
 },
 {
   "class": "ECON 305",
   "PassingStudents": 58,
   "TotalStudents": 65,
   "PassPercentage": 89.23,
   "Difficulty": "Medium"
 },
 {
   "class": "ECON 306",
   "PassingStudents": 75,
   "TotalStudents": 79,
   "PassPercentage": 94.94,
   "Difficulty": "Low"
 },
 {
   "class": "ECON 330",
   "PassingStudents": 72,
   "TotalStudents": 81,
   "PassPercentage": 88.89,
   "Difficulty": "Medium"
 },
 {
   "class": "ECON 430",
   "PassingStudents": 227,
   "TotalStudents": 237,
   "PassPercentage": 95.78,
   "Difficulty": "Low"
 },
 {
   "class": "EDCP 102",
   "PassingStudents": 72,
   "TotalStudents": 72,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "EDCP 103X",
   "PassingStudents": 24,
   "TotalStudents": 25,
   "PassPercentage": 96,
   "Difficulty": "Low"
 },
 {
   "class": "EDTC 600",
   "PassingStudents": 218,
   "TotalStudents": 272,
   "PassPercentage": 80.15,
   "Difficulty": "Medium"
 },
 {
   "class": "EDTP 635",
   "PassingStudents": 290,
   "TotalStudents": 295,
   "PassPercentage": 98.31,
   "Difficulty": "Low"
 },
 {
   "class": "EDTP 639",
   "PassingStudents": 32,
   "TotalStudents": 34,
   "PassPercentage": 94.12,
   "Difficulty": "Low"
 },
 {
   "class": "EDTP 650",
   "PassingStudents": 24,
   "TotalStudents": 24,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "EDUC 314",
   "PassingStudents": 3,
   "TotalStudents": 3,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "EMAN 600",
   "PassingStudents": 94,
   "TotalStudents": 99,
   "PassPercentage": 94.95,
   "Difficulty": "Low"
 },
 {
   "class": "EMAN 610",
   "PassingStudents": 38,
   "TotalStudents": 45,
   "PassPercentage": 84.44,
   "Difficulty": "Medium"
 },
 {
   "class": "EMAN 620",
   "PassingStudents": 19,
   "TotalStudents": 22,
   "PassPercentage": 86.36,
   "Difficulty": "Medium"
 },
 {
   "class": "EMAN 630",
   "PassingStudents": 106,
   "TotalStudents": 108,
   "PassPercentage": 98.15,
   "Difficulty": "Low"
 },
 {
   "class": "EMGT 302",
   "PassingStudents": 361,
   "TotalStudents": 397,
   "PassPercentage": 90.93,
   "Difficulty": "Low"
 },
 {
   "class": "EMGT 304",
   "PassingStudents": 42,
   "TotalStudents": 43,
   "PassPercentage": 97.67,
   "Difficulty": "Low"
 },
 {
   "class": "EMGT 306",
   "PassingStudents": 28,
   "TotalStudents": 37,
   "PassPercentage": 75.68,
   "Difficulty": "High"
 },
 {
   "class": "EMGT 308",
   "PassingStudents": 4,
   "TotalStudents": 4,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "EMGT 310",
   "PassingStudents": 18,
   "TotalStudents": 18,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "EMGT 312",
   "PassingStudents": 19,
   "TotalStudents": 20,
   "PassPercentage": 95,
   "Difficulty": "Low"
 },
 {
   "class": "EMGT 314",
   "PassingStudents": 46,
   "TotalStudents": 47,
   "PassPercentage": 97.87,
   "Difficulty": "Low"
 },
 {
   "class": "ENGL 102",
   "PassingStudents": 1184,
   "TotalStudents": 1328,
   "PassPercentage": 89.16,
   "Difficulty": "Medium"
 },
 {
   "class": "ENGL 103",
   "PassingStudents": 837,
   "TotalStudents": 987,
   "PassPercentage": 84.8,
   "Difficulty": "Medium"
 },
 {
   "class": "ENGL 205",
   "PassingStudents": 8,
   "TotalStudents": 8,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "ENGL 240",
   "PassingStudents": 355,
   "TotalStudents": 417,
   "PassPercentage": 85.13,
   "Difficulty": "Medium"
 },
 {
   "class": "ENGL 250",
   "PassingStudents": 257,
   "TotalStudents": 294,
   "PassPercentage": 87.41,
   "Difficulty": "Medium"
 },
 {
   "class": "ENGL 281",
   "PassingStudents": 238,
   "TotalStudents": 249,
   "PassPercentage": 95.58,
   "Difficulty": "Low"
 },
 {
   "class": "ENGL 294",
   "PassingStudents": 150,
   "TotalStudents": 165,
   "PassPercentage": 90.91,
   "Difficulty": "Low"
 },
 {
   "class": "ENGL 303",
   "PassingStudents": 262,
   "TotalStudents": 294,
   "PassPercentage": 89.12,
   "Difficulty": "Medium"
 },
 {
   "class": "ENGL 310",
   "PassingStudents": 223,
   "TotalStudents": 249,
   "PassPercentage": 89.56,
   "Difficulty": "Medium"
 },
 {
   "class": "ENGL 311",
   "PassingStudents": 116,
   "TotalStudents": 128,
   "PassPercentage": 90.63,
   "Difficulty": "Low"
 },
 {
   "class": "ENGL 312",
   "PassingStudents": 115,
   "TotalStudents": 127,
   "PassPercentage": 90.55,
   "Difficulty": "Low"
 },
 {
   "class": "ENGL 363",
   "PassingStudents": 98,
   "TotalStudents": 109,
   "PassPercentage": 89.91,
   "Difficulty": "Medium"
 },
 {
   "class": "ENGL 364",
   "PassingStudents": 173,
   "TotalStudents": 183,
   "PassPercentage": 94.54,
   "Difficulty": "Low"
 },
 {
   "class": "ENGL 386",
   "PassingStudents": 138,
   "TotalStudents": 151,
   "PassPercentage": 91.39,
   "Difficulty": "Low"
 },
 {
   "class": "ENGL 388J",
   "PassingStudents": 8,
   "TotalStudents": 8,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "ENGL 388Q",
   "PassingStudents": 15,
   "TotalStudents": 16,
   "PassPercentage": 93.75,
   "Difficulty": "Low"
 },
 {
   "class": "ENGL 406",
   "PassingStudents": 92,
   "TotalStudents": 96,
   "PassPercentage": 95.83,
   "Difficulty": "Low"
 },
 {
   "class": "ENGL 430",
   "PassingStudents": 190,
   "TotalStudents": 206,
   "PassPercentage": 92.23,
   "Difficulty": "Low"
 },
 {
   "class": "ENGL 433",
   "PassingStudents": 158,
   "TotalStudents": 174,
   "PassPercentage": 90.8,
   "Difficulty": "Low"
 },
 {
   "class": "ENGL 441",
   "PassingStudents": 104,
   "TotalStudents": 110,
   "PassPercentage": 94.55,
   "Difficulty": "Low"
 },
 {
   "class": "ENGL 459",
   "PassingStudents": 145,
   "TotalStudents": 158,
   "PassPercentage": 91.77,
   "Difficulty": "Low"
 },
 {
   "class": "ENGL 481",
   "PassingStudents": 10,
   "TotalStudents": 12,
   "PassPercentage": 83.33,
   "Difficulty": "Medium"
 },
 {
   "class": "ENGL 495",
   "PassingStudents": 152,
   "TotalStudents": 157,
   "PassPercentage": 96.82,
   "Difficulty": "Low"
 },
 {
   "class": "ENHS 300",
   "PassingStudents": 71,
   "TotalStudents": 77,
   "PassPercentage": 92.21,
   "Difficulty": "Low"
 },
 {
   "class": "ENHS 305",
   "PassingStudents": 80,
   "TotalStudents": 87,
   "PassPercentage": 91.95,
   "Difficulty": "Low"
 },
 {
   "class": "ENHS 310",
   "PassingStudents": 152,
   "TotalStudents": 167,
   "PassPercentage": 91.02,
   "Difficulty": "Low"
 },
 {
   "class": "ENHS 315",
   "PassingStudents": 88,
   "TotalStudents": 99,
   "PassPercentage": 88.89,
   "Difficulty": "Medium"
 },
 {
   "class": "ENHS 320",
   "PassingStudents": 52,
   "TotalStudents": 54,
   "PassPercentage": 96.3,
   "Difficulty": "Low"
 },
 {
   "class": "ENHS 325",
   "PassingStudents": 51,
   "TotalStudents": 55,
   "PassPercentage": 92.73,
   "Difficulty": "Low"
 },
 {
   "class": "ENHS 330",
   "PassingStudents": 22,
   "TotalStudents": 23,
   "PassPercentage": 95.65,
   "Difficulty": "Low"
 },
 {
   "class": "ENHS 335",
   "PassingStudents": 33,
   "TotalStudents": 33,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "ENHS 340",
   "PassingStudents": 40,
   "TotalStudents": 42,
   "PassPercentage": 95.24,
   "Difficulty": "Low"
 },
 {
   "class": "ENHS 350",
   "PassingStudents": 28,
   "TotalStudents": 29,
   "PassPercentage": 96.55,
   "Difficulty": "Low"
 },
 {
   "class": "ENHS 360",
   "PassingStudents": 28,
   "TotalStudents": 29,
   "PassPercentage": 96.55,
   "Difficulty": "Low"
 },
 {
   "class": "ENHS 400",
   "PassingStudents": 10,
   "TotalStudents": 11,
   "PassPercentage": 90.91,
   "Difficulty": "Low"
 },
 {
   "class": "ENHS 405",
   "PassingStudents": 11,
   "TotalStudents": 11,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "ENHS 495",
   "PassingStudents": 6,
   "TotalStudents": 6,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "ENMT 301",
   "PassingStudents": 93,
   "TotalStudents": 109,
   "PassPercentage": 85.32,
   "Difficulty": "Medium"
 },
 {
   "class": "ENMT 303",
   "PassingStudents": 67,
   "TotalStudents": 79,
   "PassPercentage": 84.81,
   "Difficulty": "Medium"
 },
 {
   "class": "ENMT 306",
   "PassingStudents": 61,
   "TotalStudents": 73,
   "PassPercentage": 83.56,
   "Difficulty": "Medium"
 },
 {
   "class": "ENMT 307",
   "PassingStudents": 73,
   "TotalStudents": 81,
   "PassPercentage": 90.12,
   "Difficulty": "Low"
 },
 {
   "class": "ENMT 310",
   "PassingStudents": 63,
   "TotalStudents": 65,
   "PassPercentage": 96.92,
   "Difficulty": "Low"
 },
 {
   "class": "ENMT 315",
   "PassingStudents": 32,
   "TotalStudents": 33,
   "PassPercentage": 96.97,
   "Difficulty": "Low"
 },
 {
   "class": "ENMT 321",
   "PassingStudents": 63,
   "TotalStudents": 64,
   "PassPercentage": 98.44,
   "Difficulty": "Low"
 },
 {
   "class": "ENMT 322",
   "PassingStudents": 94,
   "TotalStudents": 95,
   "PassPercentage": 98.95,
   "Difficulty": "Low"
 },
 {
   "class": "ENMT 340",
   "PassingStudents": 114,
   "TotalStudents": 120,
   "PassPercentage": 95,
   "Difficulty": "Low"
 },
 {
   "class": "ENMT 360",
   "PassingStudents": 56,
   "TotalStudents": 62,
   "PassPercentage": 90.32,
   "Difficulty": "Low"
 },
 {
   "class": "ENMT 365",
   "PassingStudents": 65,
   "TotalStudents": 78,
   "PassPercentage": 83.33,
   "Difficulty": "Medium"
 },
 {
   "class": "ENMT 380",
   "PassingStudents": 37,
   "TotalStudents": 40,
   "PassPercentage": 92.5,
   "Difficulty": "Low"
 },
 {
   "class": "ENMT 405",
   "PassingStudents": 87,
   "TotalStudents": 92,
   "PassPercentage": 94.57,
   "Difficulty": "Low"
 },
 {
   "class": "ENMT 495",
   "PassingStudents": 150,
   "TotalStudents": 158,
   "PassPercentage": 94.94,
   "Difficulty": "Low"
 },
 {
   "class": "ENVM 600",
   "PassingStudents": 49,
   "TotalStudents": 57,
   "PassPercentage": 85.96,
   "Difficulty": "Medium"
 },
 {
   "class": "ENVM 610",
   "PassingStudents": 59,
   "TotalStudents": 67,
   "PassPercentage": 88.06,
   "Difficulty": "Medium"
 },
 {
   "class": "ENVM 615",
   "PassingStudents": 49,
   "TotalStudents": 55,
   "PassPercentage": 89.09,
   "Difficulty": "Medium"
 },
 {
   "class": "ENVM 641",
   "PassingStudents": 20,
   "TotalStudents": 21,
   "PassPercentage": 95.24,
   "Difficulty": "Low"
 },
 {
   "class": "ENVM 643",
   "PassingStudents": 27,
   "TotalStudents": 30,
   "PassPercentage": 90,
   "Difficulty": "Low"
 },
 {
   "class": "ENVM 644",
   "PassingStudents": 26,
   "TotalStudents": 26,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "ENVM 647",
   "PassingStudents": 15,
   "TotalStudents": 15,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "ENVM 648",
   "PassingStudents": 11,
   "TotalStudents": 14,
   "PassPercentage": 78.57,
   "Difficulty": "High"
 },
 {
   "class": "ENVM 649",
   "PassingStudents": 18,
   "TotalStudents": 19,
   "PassPercentage": 94.74,
   "Difficulty": "Low"
 },
 {
   "class": "ENVM 651",
   "PassingStudents": 64,
   "TotalStudents": 66,
   "PassPercentage": 96.97,
   "Difficulty": "Low"
 },
 {
   "class": "ENVM 652",
   "PassingStudents": 56,
   "TotalStudents": 60,
   "PassPercentage": 93.33,
   "Difficulty": "Low"
 },
 {
   "class": "ENVM 653",
   "PassingStudents": 127,
   "TotalStudents": 131,
   "PassPercentage": 96.95,
   "Difficulty": "Low"
 },
 {
   "class": "ENVM 670",
   "PassingStudents": 57,
   "TotalStudents": 58,
   "PassPercentage": 98.28,
   "Difficulty": "Low"
 },
 {
   "class": "ERMN 000",
   "PassingStudents": 9311,
   "TotalStudents": 9586,
   "PassPercentage": 97.13,
   "Difficulty": "Low"
 },
 {
   "class": "EXCL 301",
   "PassingStudents": 68,
   "TotalStudents": 85,
   "PassPercentage": 80,
   "Difficulty": "Medium"
 },
 {
   "class": "EXCL X001",
   "PassingStudents": 14,
   "TotalStudents": 16,
   "PassPercentage": 87.5,
   "Difficulty": "Medium"
 },
 {
   "class": "FIN 605",
   "PassingStudents": 67,
   "TotalStudents": 75,
   "PassPercentage": 89.33,
   "Difficulty": "Medium"
 },
 {
   "class": "FIN 610",
   "PassingStudents": 13,
   "TotalStudents": 14,
   "PassPercentage": 92.86,
   "Difficulty": "Low"
 },
 {
   "class": "FIN 615",
   "PassingStudents": 49,
   "TotalStudents": 50,
   "PassPercentage": 98,
   "Difficulty": "Low"
 },
 {
   "class": "FIN 620",
   "PassingStudents": 115,
   "TotalStudents": 122,
   "PassPercentage": 94.26,
   "Difficulty": "Low"
 },
 {
   "class": "FIN 630",
   "PassingStudents": 70,
   "TotalStudents": 78,
   "PassPercentage": 89.74,
   "Difficulty": "Medium"
 },
 {
   "class": "FIN 645",
   "PassingStudents": 21,
   "TotalStudents": 21,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "FIN 660",
   "PassingStudents": 210,
   "TotalStudents": 212,
   "PassPercentage": 99.06,
   "Difficulty": "Low"
 },
 {
   "class": "FINC 321",
   "PassingStudents": 958,
   "TotalStudents": 1091,
   "PassPercentage": 87.81,
   "Difficulty": "Medium"
 },
 {
   "class": "FINC 328",
   "PassingStudents": 287,
   "TotalStudents": 316,
   "PassPercentage": 90.82,
   "Difficulty": "Low"
 },
 {
   "class": "FINC 330",
   "PassingStudents": 4203,
   "TotalStudents": 4696,
   "PassPercentage": 89.5,
   "Difficulty": "Medium"
 },
 {
   "class": "FINC 331",
   "PassingStudents": 1296,
   "TotalStudents": 1377,
   "PassPercentage": 94.12,
   "Difficulty": "Low"
 },
 {
   "class": "FINC 335",
   "PassingStudents": 550,
   "TotalStudents": 626,
   "PassPercentage": 87.86,
   "Difficulty": "Medium"
 },
 {
   "class": "FINC 340",
   "PassingStudents": 601,
   "TotalStudents": 653,
   "PassPercentage": 92.04,
   "Difficulty": "Low"
 },
 {
   "class": "FINC 351",
   "PassingStudents": 460,
   "TotalStudents": 488,
   "PassPercentage": 94.26,
   "Difficulty": "Low"
 },
 {
   "class": "FINC 352",
   "PassingStudents": 155,
   "TotalStudents": 166,
   "PassPercentage": 93.37,
   "Difficulty": "Low"
 },
 {
   "class": "FINC 355",
   "PassingStudents": 129,
   "TotalStudents": 142,
   "PassPercentage": 90.85,
   "Difficulty": "Low"
 },
 {
   "class": "FINC 421",
   "PassingStudents": 346,
   "TotalStudents": 371,
   "PassPercentage": 93.26,
   "Difficulty": "Low"
 },
 {
   "class": "FINC 430",
   "PassingStudents": 323,
   "TotalStudents": 344,
   "PassPercentage": 93.9,
   "Difficulty": "Low"
 },
 {
   "class": "FINC 440",
   "PassingStudents": 461,
   "TotalStudents": 490,
   "PassPercentage": 94.08,
   "Difficulty": "Low"
 },
 {
   "class": "FINC 450",
   "PassingStudents": 2,
   "TotalStudents": 2,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "FINC 460",
   "PassingStudents": 330,
   "TotalStudents": 339,
   "PassPercentage": 97.35,
   "Difficulty": "Low"
 },
 {
   "class": "FINC 490",
   "PassingStudents": 44,
   "TotalStudents": 45,
   "PassPercentage": 97.78,
   "Difficulty": "Low"
 },
 {
   "class": "FINC 495",
   "PassingStudents": 302,
   "TotalStudents": 317,
   "PassPercentage": 95.27,
   "Difficulty": "Low"
 },
 {
   "class": "FREN 111",
   "PassingStudents": 324,
   "TotalStudents": 402,
   "PassPercentage": 80.6,
   "Difficulty": "Medium"
 },
 {
   "class": "FREN 112",
   "PassingStudents": 42,
   "TotalStudents": 46,
   "PassPercentage": 91.3,
   "Difficulty": "Low"
 },
 {
   "class": "FSCN 302",
   "PassingStudents": 10,
   "TotalStudents": 17,
   "PassPercentage": 58.82,
   "Difficulty": "High"
 },
 {
   "class": "FSCN 304",
   "PassingStudents": 3,
   "TotalStudents": 3,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "FSCN 305",
   "PassingStudents": 5,
   "TotalStudents": 6,
   "PassPercentage": 83.33,
   "Difficulty": "Medium"
 },
 {
   "class": "FSCN 411",
   "PassingStudents": 13,
   "TotalStudents": 13,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "FSCN 413",
   "PassingStudents": 4,
   "TotalStudents": 4,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "FSCN 416",
   "PassingStudents": 2,
   "TotalStudents": 3,
   "PassPercentage": 66.67,
   "Difficulty": "High"
 },
 {
   "class": "GEOG 100",
   "PassingStudents": 617,
   "TotalStudents": 661,
   "PassPercentage": 93.34,
   "Difficulty": "Low"
 },
 {
   "class": "GEOL 100",
   "PassingStudents": 826,
   "TotalStudents": 905,
   "PassPercentage": 91.27,
   "Difficulty": "Low"
 },
 {
   "class": "GEOL 110",
   "PassingStudents": 144,
   "TotalStudents": 145,
   "PassPercentage": 99.31,
   "Difficulty": "Low"
 },
 {
   "class": "GERM 111",
   "PassingStudents": 716,
   "TotalStudents": 796,
   "PassPercentage": 89.95,
   "Difficulty": "Medium"
 },
 {
   "class": "GERM 112",
   "PassingStudents": 245,
   "TotalStudents": 269,
   "PassPercentage": 91.08,
   "Difficulty": "Low"
 },
 {
   "class": "GERM 211",
   "PassingStudents": 109,
   "TotalStudents": 112,
   "PassPercentage": 97.32,
   "Difficulty": "Low"
 },
 {
   "class": "GERM 212",
   "PassingStudents": 71,
   "TotalStudents": 71,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "GERM 311",
   "PassingStudents": 30,
   "TotalStudents": 33,
   "PassPercentage": 90.91,
   "Difficulty": "Low"
 },
 {
   "class": "GERM 314",
   "PassingStudents": 47,
   "TotalStudents": 50,
   "PassPercentage": 94,
   "Difficulty": "Low"
 },
 {
   "class": "GERM 334",
   "PassingStudents": 15,
   "TotalStudents": 15,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "GERO 100",
   "PassingStudents": 311,
   "TotalStudents": 350,
   "PassPercentage": 88.86,
   "Difficulty": "Medium"
 },
 {
   "class": "GERO 301",
   "PassingStudents": 74,
   "TotalStudents": 83,
   "PassPercentage": 89.16,
   "Difficulty": "Medium"
 },
 {
   "class": "GERO 302",
   "PassingStudents": 218,
   "TotalStudents": 240,
   "PassPercentage": 90.83,
   "Difficulty": "Low"
 },
 {
   "class": "GERO 306",
   "PassingStudents": 52,
   "TotalStudents": 57,
   "PassPercentage": 91.23,
   "Difficulty": "Low"
 },
 {
   "class": "GERO 311",
   "PassingStudents": 80,
   "TotalStudents": 83,
   "PassPercentage": 96.39,
   "Difficulty": "Low"
 },
 {
   "class": "GERO 320",
   "PassingStudents": 140,
   "TotalStudents": 152,
   "PassPercentage": 92.11,
   "Difficulty": "Low"
 },
 {
   "class": "GERO 338",
   "PassingStudents": 51,
   "TotalStudents": 53,
   "PassPercentage": 96.23,
   "Difficulty": "Low"
 },
 {
   "class": "GERO 342",
   "PassingStudents": 62,
   "TotalStudents": 64,
   "PassPercentage": 96.88,
   "Difficulty": "Low"
 },
 {
   "class": "GERO 390",
   "PassingStudents": 46,
   "TotalStudents": 55,
   "PassPercentage": 83.64,
   "Difficulty": "Medium"
 },
 {
   "class": "GERO 427",
   "PassingStudents": 71,
   "TotalStudents": 78,
   "PassPercentage": 91.03,
   "Difficulty": "Low"
 },
 {
   "class": "GERO 486A",
   "PassingStudents": 15,
   "TotalStudents": 17,
   "PassPercentage": 88.24,
   "Difficulty": "Medium"
 },
 {
   "class": "GERO 486B",
   "PassingStudents": 1,
   "TotalStudents": 1,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "GRCO 100",
   "PassingStudents": 698,
   "TotalStudents": 851,
   "PassPercentage": 82.02,
   "Difficulty": "Medium"
 },
 {
   "class": "GRCO 230",
   "PassingStudents": 205,
   "TotalStudents": 240,
   "PassPercentage": 85.42,
   "Difficulty": "Medium"
 },
 {
   "class": "GRCO 350",
   "PassingStudents": 162,
   "TotalStudents": 183,
   "PassPercentage": 88.52,
   "Difficulty": "Medium"
 },
 {
   "class": "GRCO 354",
   "PassingStudents": 184,
   "TotalStudents": 213,
   "PassPercentage": 86.38,
   "Difficulty": "Medium"
 },
 {
   "class": "GRCO 355",
   "PassingStudents": 448,
   "TotalStudents": 510,
   "PassPercentage": 87.84,
   "Difficulty": "Medium"
 },
 {
   "class": "GRCO 450",
   "PassingStudents": 110,
   "TotalStudents": 122,
   "PassPercentage": 90.16,
   "Difficulty": "Low"
 },
 {
   "class": "GRCO 479",
   "PassingStudents": 179,
   "TotalStudents": 203,
   "PassPercentage": 88.18,
   "Difficulty": "Medium"
 },
 {
   "class": "GRCO 495",
   "PassingStudents": 143,
   "TotalStudents": 160,
   "PassPercentage": 89.38,
   "Difficulty": "Medium"
 },
 {
   "class": "GVPT 100",
   "PassingStudents": 602,
   "TotalStudents": 693,
   "PassPercentage": 86.87,
   "Difficulty": "Medium"
 },
 {
   "class": "GVPT 101",
   "PassingStudents": 337,
   "TotalStudents": 393,
   "PassPercentage": 85.75,
   "Difficulty": "Medium"
 },
 {
   "class": "GVPT 170",
   "PassingStudents": 978,
   "TotalStudents": 1080,
   "PassPercentage": 90.56,
   "Difficulty": "Low"
 },
 {
   "class": "GVPT 200",
   "PassingStudents": 161,
   "TotalStudents": 174,
   "PassPercentage": 92.53,
   "Difficulty": "Low"
 },
 {
   "class": "GVPT 210",
   "PassingStudents": 148,
   "TotalStudents": 168,
   "PassPercentage": 88.1,
   "Difficulty": "Medium"
 },
 {
   "class": "GVPT 280",
   "PassingStudents": 226,
   "TotalStudents": 272,
   "PassPercentage": 83.09,
   "Difficulty": "Medium"
 },
 {
   "class": "GVPT 306",
   "PassingStudents": 338,
   "TotalStudents": 365,
   "PassPercentage": 92.6,
   "Difficulty": "Low"
 },
 {
   "class": "GVPT 308",
   "PassingStudents": 167,
   "TotalStudents": 188,
   "PassPercentage": 88.83,
   "Difficulty": "Medium"
 },
 {
   "class": "GVPT 399O",
   "PassingStudents": 17,
   "TotalStudents": 17,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "GVPT 403",
   "PassingStudents": 192,
   "TotalStudents": 206,
   "PassPercentage": 93.2,
   "Difficulty": "Low"
 },
 {
   "class": "GVPT 406",
   "PassingStudents": 333,
   "TotalStudents": 383,
   "PassPercentage": 86.95,
   "Difficulty": "Medium"
 },
 {
   "class": "GVPT 407",
   "PassingStudents": 79,
   "TotalStudents": 82,
   "PassPercentage": 96.34,
   "Difficulty": "Low"
 },
 {
   "class": "GVPT 408",
   "PassingStudents": 149,
   "TotalStudents": 153,
   "PassPercentage": 97.39,
   "Difficulty": "Low"
 },
 {
   "class": "GVPT 409",
   "PassingStudents": 139,
   "TotalStudents": 153,
   "PassPercentage": 90.85,
   "Difficulty": "Low"
 },
 {
   "class": "GVPT 444",
   "PassingStudents": 62,
   "TotalStudents": 64,
   "PassPercentage": 96.88,
   "Difficulty": "Low"
 },
 {
   "class": "GVPT 457",
   "PassingStudents": 161,
   "TotalStudents": 174,
   "PassPercentage": 92.53,
   "Difficulty": "Low"
 },
 {
   "class": "GVPT 475",
   "PassingStudents": 70,
   "TotalStudents": 75,
   "PassPercentage": 93.33,
   "Difficulty": "Low"
 },
 {
   "class": "GVPT 495",
   "PassingStudents": 192,
   "TotalStudents": 198,
   "PassPercentage": 96.97,
   "Difficulty": "Low"
 },
 {
   "class": "HCAD 600",
   "PassingStudents": 250,
   "TotalStudents": 291,
   "PassPercentage": 85.91,
   "Difficulty": "Medium"
 },
 {
   "class": "HCAD 610",
   "PassingStudents": 13,
   "TotalStudents": 15,
   "PassPercentage": 86.67,
   "Difficulty": "Medium"
 },
 {
   "class": "HCAD 620",
   "PassingStudents": 92,
   "TotalStudents": 96,
   "PassPercentage": 95.83,
   "Difficulty": "Low"
 },
 {
   "class": "HCAD 630",
   "PassingStudents": 596,
   "TotalStudents": 610,
   "PassPercentage": 97.7,
   "Difficulty": "Low"
 },
 {
   "class": "HCAD 650",
   "PassingStudents": 37,
   "TotalStudents": 38,
   "PassPercentage": 97.37,
   "Difficulty": "Low"
 },
 {
   "class": "HCAD 660",
   "PassingStudents": 30,
   "TotalStudents": 31,
   "PassPercentage": 96.77,
   "Difficulty": "Low"
 },
 {
   "class": "HCAD 670",
   "PassingStudents": 10,
   "TotalStudents": 10,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "HIMS 650",
   "PassingStudents": 40,
   "TotalStudents": 45,
   "PassPercentage": 88.89,
   "Difficulty": "Medium"
 },
 {
   "class": "HIMS 661",
   "PassingStudents": 15,
   "TotalStudents": 15,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 115",
   "PassingStudents": 1378,
   "TotalStudents": 1590,
   "PassPercentage": 86.67,
   "Difficulty": "Medium"
 },
 {
   "class": "HIST 116",
   "PassingStudents": 383,
   "TotalStudents": 416,
   "PassPercentage": 92.07,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 125",
   "PassingStudents": 1905,
   "TotalStudents": 2180,
   "PassPercentage": 87.39,
   "Difficulty": "Medium"
 },
 {
   "class": "HIST 141",
   "PassingStudents": 348,
   "TotalStudents": 393,
   "PassPercentage": 88.55,
   "Difficulty": "Medium"
 },
 {
   "class": "HIST 142",
   "PassingStudents": 143,
   "TotalStudents": 155,
   "PassPercentage": 92.26,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 156",
   "PassingStudents": 1622,
   "TotalStudents": 1796,
   "PassPercentage": 90.31,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 157",
   "PassingStudents": 896,
   "TotalStudents": 981,
   "PassPercentage": 91.34,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 202",
   "PassingStudents": 395,
   "TotalStudents": 430,
   "PassPercentage": 91.86,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 219",
   "PassingStudents": 6,
   "TotalStudents": 6,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 289",
   "PassingStudents": 267,
   "TotalStudents": 314,
   "PassPercentage": 85.03,
   "Difficulty": "Medium"
 },
 {
   "class": "HIST 309",
   "PassingStudents": 244,
   "TotalStudents": 268,
   "PassPercentage": 91.04,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 316L",
   "PassingStudents": 194,
   "TotalStudents": 204,
   "PassPercentage": 95.1,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 316N",
   "PassingStudents": 1,
   "TotalStudents": 1,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 326",
   "PassingStudents": 391,
   "TotalStudents": 417,
   "PassPercentage": 93.76,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 337",
   "PassingStudents": 169,
   "TotalStudents": 183,
   "PassPercentage": 92.35,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 365",
   "PassingStudents": 400,
   "TotalStudents": 432,
   "PassPercentage": 92.59,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 377",
   "PassingStudents": 319,
   "TotalStudents": 348,
   "PassPercentage": 91.67,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 381",
   "PassingStudents": 129,
   "TotalStudents": 132,
   "PassPercentage": 97.73,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 392",
   "PassingStudents": 121,
   "TotalStudents": 132,
   "PassPercentage": 91.67,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 461",
   "PassingStudents": 216,
   "TotalStudents": 238,
   "PassPercentage": 90.76,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 462",
   "PassingStudents": 305,
   "TotalStudents": 320,
   "PassPercentage": 95.31,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 464",
   "PassingStudents": 198,
   "TotalStudents": 215,
   "PassPercentage": 92.09,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 465",
   "PassingStudents": 449,
   "TotalStudents": 479,
   "PassPercentage": 93.74,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 480",
   "PassingStudents": 78,
   "TotalStudents": 87,
   "PassPercentage": 89.66,
   "Difficulty": "Medium"
 },
 {
   "class": "HIST 482",
   "PassingStudents": 190,
   "TotalStudents": 204,
   "PassPercentage": 93.14,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 483",
   "PassingStudents": 129,
   "TotalStudents": 142,
   "PassPercentage": 90.85,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 495",
   "PassingStudents": 205,
   "TotalStudents": 207,
   "PassPercentage": 99.03,
   "Difficulty": "Low"
 },
 {
   "class": "HIST 602",
   "PassingStudents": 1,
   "TotalStudents": 1,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "HMGT 300",
   "PassingStudents": 1295,
   "TotalStudents": 1577,
   "PassPercentage": 82.12,
   "Difficulty": "Medium"
 },
 {
   "class": "HMGT 307",
   "PassingStudents": 967,
   "TotalStudents": 1103,
   "PassPercentage": 87.67,
   "Difficulty": "Medium"
 },
 {
   "class": "HMGT 310",
   "PassingStudents": 776,
   "TotalStudents": 866,
   "PassPercentage": 89.61,
   "Difficulty": "Medium"
 },
 {
   "class": "HMGT 320",
   "PassingStudents": 828,
   "TotalStudents": 886,
   "PassPercentage": 93.45,
   "Difficulty": "Low"
 },
 {
   "class": "HMGT 322",
   "PassingStudents": 1136,
   "TotalStudents": 1245,
   "PassPercentage": 91.24,
   "Difficulty": "Low"
 },
 {
   "class": "HMGT 335",
   "PassingStudents": 1617,
   "TotalStudents": 1767,
   "PassPercentage": 91.51,
   "Difficulty": "Low"
 },
 {
   "class": "HMGT 372",
   "PassingStudents": 1404,
   "TotalStudents": 1580,
   "PassPercentage": 88.86,
   "Difficulty": "Medium"
 },
 {
   "class": "HMGT 400",
   "PassingStudents": 465,
   "TotalStudents": 532,
   "PassPercentage": 87.41,
   "Difficulty": "Medium"
 },
 {
   "class": "HMGT 420",
   "PassingStudents": 411,
   "TotalStudents": 469,
   "PassPercentage": 87.63,
   "Difficulty": "Medium"
 },
 {
   "class": "HMGT 435",
   "PassingStudents": 587,
   "TotalStudents": 638,
   "PassPercentage": 92.01,
   "Difficulty": "Low"
 },
 {
   "class": "HMGT 495",
   "PassingStudents": 722,
   "TotalStudents": 759,
   "PassPercentage": 95.13,
   "Difficulty": "Low"
 },
 {
   "class": "HMLS 302",
   "PassingStudents": 621,
   "TotalStudents": 669,
   "PassPercentage": 92.83,
   "Difficulty": "Low"
 },
 {
   "class": "HMLS 304",
   "PassingStudents": 233,
   "TotalStudents": 255,
   "PassPercentage": 91.37,
   "Difficulty": "Low"
 },
 {
   "class": "HMLS 310",
   "PassingStudents": 294,
   "TotalStudents": 304,
   "PassPercentage": 96.71,
   "Difficulty": "Low"
 },
 {
   "class": "HMLS 406",
   "PassingStudents": 386,
   "TotalStudents": 420,
   "PassPercentage": 91.9,
   "Difficulty": "Low"
 },
 {
   "class": "HMLS 408",
   "PassingStudents": 318,
   "TotalStudents": 336,
   "PassPercentage": 94.64,
   "Difficulty": "Low"
 },
 {
   "class": "HMLS 414",
   "PassingStudents": 303,
   "TotalStudents": 323,
   "PassPercentage": 93.81,
   "Difficulty": "Low"
 },
 {
   "class": "HMLS 416",
   "PassingStudents": 307,
   "TotalStudents": 315,
   "PassPercentage": 97.46,
   "Difficulty": "Low"
 },
 {
   "class": "HMLS 495",
   "PassingStudents": 232,
   "TotalStudents": 240,
   "PassPercentage": 96.67,
   "Difficulty": "Low"
 },
 {
   "class": "HRMD 610",
   "PassingStudents": 299,
   "TotalStudents": 406,
   "PassPercentage": 73.65,
   "Difficulty": "High"
 },
 {
   "class": "HRMD 620",
   "PassingStudents": 99,
   "TotalStudents": 195,
   "PassPercentage": 50.77,
   "Difficulty": "High"
 },
 {
   "class": "HRMD 630",
   "PassingStudents": 580,
   "TotalStudents": 660,
   "PassPercentage": 87.88,
   "Difficulty": "Medium"
 },
 {
   "class": "HRMD 640",
   "PassingStudents": 110,
   "TotalStudents": 182,
   "PassPercentage": 60.44,
   "Difficulty": "High"
 },
 {
   "class": "HRMD 650",
   "PassingStudents": 624,
   "TotalStudents": 693,
   "PassPercentage": 90.04,
   "Difficulty": "Low"
 },
 {
   "class": "HRMD 651",
   "PassingStudents": 203,
   "TotalStudents": 208,
   "PassPercentage": 97.6,
   "Difficulty": "Low"
 },
 {
   "class": "HRMD 665",
   "PassingStudents": 62,
   "TotalStudents": 62,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "HRMN 300",
   "PassingStudents": 3745,
   "TotalStudents": 4103,
   "PassPercentage": 91.27,
   "Difficulty": "Low"
 },
 {
   "class": "HRMN 302",
   "PassingStudents": 1533,
   "TotalStudents": 1652,
   "PassPercentage": 92.8,
   "Difficulty": "Low"
 },
 {
   "class": "HRMN 362",
   "PassingStudents": 1186,
   "TotalStudents": 1278,
   "PassPercentage": 92.8,
   "Difficulty": "Low"
 },
 {
   "class": "HRMN 367",
   "PassingStudents": 1152,
   "TotalStudents": 1247,
   "PassPercentage": 92.38,
   "Difficulty": "Low"
 },
 {
   "class": "HRMN 395",
   "PassingStudents": 1602,
   "TotalStudents": 1736,
   "PassPercentage": 92.28,
   "Difficulty": "Low"
 },
 {
   "class": "HRMN 400",
   "PassingStudents": 2775,
   "TotalStudents": 2963,
   "PassPercentage": 93.66,
   "Difficulty": "Low"
 },
 {
   "class": "HRMN 406",
   "PassingStudents": 901,
   "TotalStudents": 946,
   "PassPercentage": 95.24,
   "Difficulty": "Low"
 },
 {
   "class": "HRMN 408",
   "PassingStudents": 784,
   "TotalStudents": 833,
   "PassPercentage": 94.12,
   "Difficulty": "Low"
 },
 {
   "class": "HRMN 410",
   "PassingStudents": 81,
   "TotalStudents": 84,
   "PassPercentage": 96.43,
   "Difficulty": "Low"
 },
 {
   "class": "HRMN 467",
   "PassingStudents": 658,
   "TotalStudents": 675,
   "PassPercentage": 97.48,
   "Difficulty": "Low"
 },
 {
   "class": "HRMN 486A",
   "PassingStudents": 2,
   "TotalStudents": 2,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "HRMN 486B",
   "PassingStudents": 4,
   "TotalStudents": 4,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "HRMN 495",
   "PassingStudents": 1568,
   "TotalStudents": 1617,
   "PassPercentage": 96.97,
   "Difficulty": "Low"
 },
 {
   "class": "HSMN 610",
   "PassingStudents": 176,
   "TotalStudents": 189,
   "PassPercentage": 93.12,
   "Difficulty": "Low"
 },
 {
   "class": "HSMN 625",
   "PassingStudents": 0,
   "TotalStudents": 9,
   "PassPercentage": 0,
   "Difficulty": "High"
 },
 {
   "class": "HSMN 630",
   "PassingStudents": 206,
   "TotalStudents": 216,
   "PassPercentage": 95.37,
   "Difficulty": "Low"
 },
 {
   "class": "HSMN 670",
   "PassingStudents": 264,
   "TotalStudents": 265,
   "PassPercentage": 99.62,
   "Difficulty": "Low"
 },
 {
   "class": "HUMN 100",
   "PassingStudents": 3407,
   "TotalStudents": 4508,
   "PassPercentage": 75.58,
   "Difficulty": "High"
 },
 {
   "class": "HUMN 344",
   "PassingStudents": 1243,
   "TotalStudents": 1466,
   "PassPercentage": 84.79,
   "Difficulty": "Medium"
 },
 {
   "class": "HUMN 351",
   "PassingStudents": 828,
   "TotalStudents": 1024,
   "PassPercentage": 80.86,
   "Difficulty": "Medium"
 },
 {
   "class": "HUMN 495",
   "PassingStudents": 63,
   "TotalStudents": 65,
   "PassPercentage": 96.92,
   "Difficulty": "Low"
 },
 {
   "class": "IFSM 201",
   "PassingStudents": 8212,
   "TotalStudents": 9541,
   "PassPercentage": 86.07,
   "Difficulty": "Medium"
 },
 {
   "class": "IFSM 300",
   "PassingStudents": 5980,
   "TotalStudents": 6764,
   "PassPercentage": 88.41,
   "Difficulty": "Medium"
 },
 {
   "class": "IFSM 301",
   "PassingStudents": 713,
   "TotalStudents": 787,
   "PassPercentage": 90.6,
   "Difficulty": "Low"
 },
 {
   "class": "IFSM 304",
   "PassingStudents": 1563,
   "TotalStudents": 1698,
   "PassPercentage": 92.05,
   "Difficulty": "Low"
 },
 {
   "class": "IFSM 305",
   "PassingStudents": 1008,
   "TotalStudents": 1209,
   "PassPercentage": 83.37,
   "Difficulty": "Medium"
 },
 {
   "class": "IFSM 310",
   "PassingStudents": 541,
   "TotalStudents": 564,
   "PassPercentage": 95.92,
   "Difficulty": "Low"
 },
 {
   "class": "IFSM 311",
   "PassingStudents": 477,
   "TotalStudents": 513,
   "PassPercentage": 92.98,
   "Difficulty": "Low"
 },
 {
   "class": "IFSM 330",
   "PassingStudents": 982,
   "TotalStudents": 1064,
   "PassPercentage": 92.29,
   "Difficulty": "Low"
 },
 {
   "class": "IFSM 370",
   "PassingStudents": 1346,
   "TotalStudents": 1406,
   "PassPercentage": 95.73,
   "Difficulty": "Low"
 },
 {
   "class": "IFSM 380",
   "PassingStudents": 58,
   "TotalStudents": 61,
   "PassPercentage": 95.08,
   "Difficulty": "Low"
 },
 {
   "class": "IFSM 432",
   "PassingStudents": 100,
   "TotalStudents": 106,
   "PassPercentage": 94.34,
   "Difficulty": "Low"
 },
 {
   "class": "IFSM 438",
   "PassingStudents": 673,
   "TotalStudents": 701,
   "PassPercentage": 96.01,
   "Difficulty": "Low"
 },
 {
   "class": "IFSM 441",
   "PassingStudents": 172,
   "TotalStudents": 175,
   "PassPercentage": 98.29,
   "Difficulty": "Low"
 },
 {
   "class": "IFSM 461",
   "PassingStudents": 410,
   "TotalStudents": 432,
   "PassPercentage": 94.91,
   "Difficulty": "Low"
 },
 {
   "class": "IFSM 486B",
   "PassingStudents": 1,
   "TotalStudents": 1,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "IFSM 495",
   "PassingStudents": 539,
   "TotalStudents": 548,
   "PassPercentage": 98.36,
   "Difficulty": "Low"
 },
 {
   "class": "INFA 610",
   "PassingStudents": 20,
   "TotalStudents": 20,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "INFA 620",
   "PassingStudents": 15,
   "TotalStudents": 15,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "INFA 650",
   "PassingStudents": 21,
   "TotalStudents": 22,
   "PassPercentage": 95.45,
   "Difficulty": "Low"
 },
 {
   "class": "INFA 660",
   "PassingStudents": 7,
   "TotalStudents": 7,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "INFA 670",
   "PassingStudents": 1,
   "TotalStudents": 1,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "INST 605",
   "PassingStudents": 45,
   "TotalStudents": 58,
   "PassPercentage": 77.59,
   "Difficulty": "High"
 },
 {
   "class": "ITAL 111",
   "PassingStudents": 69,
   "TotalStudents": 72,
   "PassPercentage": 95.83,
   "Difficulty": "Low"
 },
 {
   "class": "ITAL 112",
   "PassingStudents": 10,
   "TotalStudents": 10,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "ITAL 211",
   "PassingStudents": 27,
   "TotalStudents": 27,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "ITAL 212",
   "PassingStudents": 15,
   "TotalStudents": 15,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "ITAL 333",
   "PassingStudents": 13,
   "TotalStudents": 13,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "ITEC 620",
   "PassingStudents": 20,
   "TotalStudents": 21,
   "PassPercentage": 95.24,
   "Difficulty": "Low"
 },
 {
   "class": "ITEC 625",
   "PassingStudents": 630,
   "TotalStudents": 671,
   "PassPercentage": 93.89,
   "Difficulty": "Low"
 },
 {
   "class": "ITEC 626",
   "PassingStudents": 506,
   "TotalStudents": 529,
   "PassPercentage": 95.65,
   "Difficulty": "Low"
 },
 {
   "class": "ITEC 630",
   "PassingStudents": 217,
   "TotalStudents": 230,
   "PassPercentage": 94.35,
   "Difficulty": "Low"
 },
 {
   "class": "ITEC 640",
   "PassingStudents": 25,
   "TotalStudents": 26,
   "PassPercentage": 96.15,
   "Difficulty": "Low"
 },
 {
   "class": "JAPN 111",
   "PassingStudents": 1643,
   "TotalStudents": 1991,
   "PassPercentage": 82.52,
   "Difficulty": "Medium"
 },
 {
   "class": "JAPN 112",
   "PassingStudents": 509,
   "TotalStudents": 583,
   "PassPercentage": 87.31,
   "Difficulty": "Medium"
 },
 {
   "class": "JAPN 114",
   "PassingStudents": 208,
   "TotalStudents": 253,
   "PassPercentage": 82.21,
   "Difficulty": "Medium"
 },
 {
   "class": "JAPN 115",
   "PassingStudents": 70,
   "TotalStudents": 81,
   "PassPercentage": 86.42,
   "Difficulty": "Medium"
 },
 {
   "class": "JAPN 221",
   "PassingStudents": 36,
   "TotalStudents": 40,
   "PassPercentage": 90,
   "Difficulty": "Low"
 },
 {
   "class": "JAPN 222",
   "PassingStudents": 17,
   "TotalStudents": 18,
   "PassPercentage": 94.44,
   "Difficulty": "Low"
 },
 {
   "class": "JAPN 333",
   "PassingStudents": 319,
   "TotalStudents": 351,
   "PassPercentage": 90.88,
   "Difficulty": "Low"
 },
 {
   "class": "JOUR 201",
   "PassingStudents": 662,
   "TotalStudents": 829,
   "PassPercentage": 79.86,
   "Difficulty": "High"
 },
 {
   "class": "JOUR 330",
   "PassingStudents": 259,
   "TotalStudents": 279,
   "PassPercentage": 92.83,
   "Difficulty": "Low"
 },
 {
   "class": "KORN 111",
   "PassingStudents": 80,
   "TotalStudents": 88,
   "PassPercentage": 90.91,
   "Difficulty": "Low"
 },
 {
   "class": "KORN 112",
   "PassingStudents": 33,
   "TotalStudents": 34,
   "PassPercentage": 97.06,
   "Difficulty": "Low"
 },
 {
   "class": "KORN 115",
   "PassingStudents": 4,
   "TotalStudents": 4,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "KORN 221",
   "PassingStudents": 5,
   "TotalStudents": 5,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "KORN 333",
   "PassingStudents": 75,
   "TotalStudents": 86,
   "PassPercentage": 87.21,
   "Difficulty": "Medium"
 },
 {
   "class": "LGST 101",
   "PassingStudents": 474,
   "TotalStudents": 549,
   "PassPercentage": 86.34,
   "Difficulty": "Medium"
 },
 {
   "class": "LGST 200",
   "PassingStudents": 315,
   "TotalStudents": 385,
   "PassPercentage": 81.82,
   "Difficulty": "Medium"
 },
 {
   "class": "LGST 201",
   "PassingStudents": 205,
   "TotalStudents": 233,
   "PassPercentage": 87.98,
   "Difficulty": "Medium"
 },
 {
   "class": "LGST 204",
   "PassingStudents": 226,
   "TotalStudents": 250,
   "PassPercentage": 90.4,
   "Difficulty": "Low"
 },
 {
   "class": "LGST 300",
   "PassingStudents": 25,
   "TotalStudents": 26,
   "PassPercentage": 96.15,
   "Difficulty": "Low"
 },
 {
   "class": "LGST 301",
   "PassingStudents": 205,
   "TotalStudents": 216,
   "PassPercentage": 94.91,
   "Difficulty": "Low"
 },
 {
   "class": "LGST 312",
   "PassingStudents": 230,
   "TotalStudents": 242,
   "PassPercentage": 95.04,
   "Difficulty": "Low"
 },
 {
   "class": "LGST 314",
   "PassingStudents": 72,
   "TotalStudents": 76,
   "PassPercentage": 94.74,
   "Difficulty": "Low"
 },
 {
   "class": "LGST 315",
   "PassingStudents": 174,
   "TotalStudents": 192,
   "PassPercentage": 90.63,
   "Difficulty": "Low"
 },
 {
   "class": "LGST 316",
   "PassingStudents": 29,
   "TotalStudents": 30,
   "PassPercentage": 96.67,
   "Difficulty": "Low"
 },
 {
   "class": "LGST 320",
   "PassingStudents": 188,
   "TotalStudents": 198,
   "PassPercentage": 94.95,
   "Difficulty": "Low"
 },
 {
   "class": "LGST 325",
   "PassingStudents": 182,
   "TotalStudents": 198,
   "PassPercentage": 91.92,
   "Difficulty": "Low"
 },
 {
   "class": "LGST 327",
   "PassingStudents": 66,
   "TotalStudents": 70,
   "PassPercentage": 94.29,
   "Difficulty": "Low"
 },
 {
   "class": "LGST 330",
   "PassingStudents": 24,
   "TotalStudents": 25,
   "PassPercentage": 96,
   "Difficulty": "Low"
 },
 {
   "class": "LGST 340",
   "PassingStudents": 189,
   "TotalStudents": 196,
   "PassPercentage": 96.43,
   "Difficulty": "Low"
 },
 {
   "class": "LGST 486B",
   "PassingStudents": 1,
   "TotalStudents": 1,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "LGST 495",
   "PassingStudents": 170,
   "TotalStudents": 176,
   "PassPercentage": 96.59,
   "Difficulty": "Low"
 },
 {
   "class": "LIBS 150",
   "PassingStudents": 22802,
   "TotalStudents": 24789,
   "PassPercentage": 91.98,
   "Difficulty": "Low"
 },
 {
   "class": "MATH 009",
   "PassingStudents": 4616,
   "TotalStudents": 5431,
   "PassPercentage": 84.99,
   "Difficulty": "Medium"
 },
 {
   "class": "MATH 012",
   "PassingStudents": 4778,
   "TotalStudents": 5316,
   "PassPercentage": 89.88,
   "Difficulty": "Medium"
 },
 {
   "class": "MATH 103",
   "PassingStudents": 875,
   "TotalStudents": 999,
   "PassPercentage": 87.59,
   "Difficulty": "Medium"
 },
 {
   "class": "MATH 105",
   "PassingStudents": 10709,
   "TotalStudents": 12517,
   "PassPercentage": 85.56,
   "Difficulty": "Medium"
 },
 {
   "class": "MATH 106",
   "PassingStudents": 1652,
   "TotalStudents": 1895,
   "PassPercentage": 87.18,
   "Difficulty": "Medium"
 },
 {
   "class": "MATH 107",
   "PassingStudents": 12014,
   "TotalStudents": 13627,
   "PassPercentage": 88.16,
   "Difficulty": "Medium"
 },
 {
   "class": "MATH 108",
   "PassingStudents": 961,
   "TotalStudents": 1087,
   "PassPercentage": 88.41,
   "Difficulty": "Medium"
 },
 {
   "class": "MATH 115",
   "PassingStudents": 2816,
   "TotalStudents": 3248,
   "PassPercentage": 86.7,
   "Difficulty": "Medium"
 },
 {
   "class": "MATH 140",
   "PassingStudents": 1345,
   "TotalStudents": 1551,
   "PassPercentage": 86.72,
   "Difficulty": "Medium"
 },
 {
   "class": "MATH 141",
   "PassingStudents": 910,
   "TotalStudents": 999,
   "PassPercentage": 91.09,
   "Difficulty": "Low"
 },
 {
   "class": "MATH 241",
   "PassingStudents": 129,
   "TotalStudents": 142,
   "PassPercentage": 90.85,
   "Difficulty": "Low"
 },
 {
   "class": "MATH 246",
   "PassingStudents": 76,
   "TotalStudents": 84,
   "PassPercentage": 90.48,
   "Difficulty": "Low"
 },
 {
   "class": "MATH 301",
   "PassingStudents": 73,
   "TotalStudents": 86,
   "PassPercentage": 84.88,
   "Difficulty": "Medium"
 },
 {
   "class": "MATH 340",
   "PassingStudents": 84,
   "TotalStudents": 96,
   "PassPercentage": 87.5,
   "Difficulty": "Medium"
 },
 {
   "class": "MATH 402",
   "PassingStudents": 9,
   "TotalStudents": 9,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "MATH X037",
   "PassingStudents": 61,
   "TotalStudents": 72,
   "PassPercentage": 84.72,
   "Difficulty": "Medium"
 },
 {
   "class": "MGMT 610",
   "PassingStudents": 67,
   "TotalStudents": 71,
   "PassPercentage": 94.37,
   "Difficulty": "Low"
 },
 {
   "class": "MGMT 630",
   "PassingStudents": 16,
   "TotalStudents": 20,
   "PassPercentage": 80,
   "Difficulty": "Medium"
 },
 {
   "class": "MGMT 640",
   "PassingStudents": 153,
   "TotalStudents": 177,
   "PassPercentage": 86.44,
   "Difficulty": "Medium"
 },
 {
   "class": "MGMT 650",
   "PassingStudents": 598,
   "TotalStudents": 632,
   "PassPercentage": 94.62,
   "Difficulty": "Low"
 },
 {
   "class": "MRKT 310",
   "PassingStudents": 5198,
   "TotalStudents": 5725,
   "PassPercentage": 90.79,
   "Difficulty": "Low"
 },
 {
   "class": "MRKT 311",
   "PassingStudents": 540,
   "TotalStudents": 591,
   "PassPercentage": 91.37,
   "Difficulty": "Low"
 },
 {
   "class": "MRKT 314",
   "PassingStudents": 309,
   "TotalStudents": 326,
   "PassPercentage": 94.79,
   "Difficulty": "Low"
 },
 {
   "class": "MRKT 354",
   "PassingStudents": 592,
   "TotalStudents": 671,
   "PassPercentage": 88.23,
   "Difficulty": "Medium"
 },
 {
   "class": "MRKT 356",
   "PassingStudents": 131,
   "TotalStudents": 139,
   "PassPercentage": 94.24,
   "Difficulty": "Low"
 },
 {
   "class": "MRKT 394",
   "PassingStudents": 346,
   "TotalStudents": 367,
   "PassPercentage": 94.28,
   "Difficulty": "Low"
 },
 {
   "class": "MRKT 395",
   "PassingStudents": 393,
   "TotalStudents": 410,
   "PassPercentage": 95.85,
   "Difficulty": "Low"
 },
 {
   "class": "MRKT 410",
   "PassingStudents": 271,
   "TotalStudents": 305,
   "PassPercentage": 88.85,
   "Difficulty": "Medium"
 },
 {
   "class": "MRKT 411",
   "PassingStudents": 147,
   "TotalStudents": 155,
   "PassPercentage": 94.84,
   "Difficulty": "Low"
 },
 {
   "class": "MRKT 412",
   "PassingStudents": 285,
   "TotalStudents": 302,
   "PassPercentage": 94.37,
   "Difficulty": "Low"
 },
 {
   "class": "MRKT 454",
   "PassingStudents": 333,
   "TotalStudents": 356,
   "PassPercentage": 93.54,
   "Difficulty": "Low"
 },
 {
   "class": "MRKT 458",
   "PassingStudents": 399,
   "TotalStudents": 419,
   "PassPercentage": 95.23,
   "Difficulty": "Low"
 },
 {
   "class": "MRKT 475",
   "PassingStudents": 92,
   "TotalStudents": 98,
   "PassPercentage": 93.88,
   "Difficulty": "Low"
 },
 {
   "class": "MRKT 486A",
   "PassingStudents": 1,
   "TotalStudents": 1,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "MRKT 486B",
   "PassingStudents": 2,
   "TotalStudents": 2,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "MRKT 495",
   "PassingStudents": 593,
   "TotalStudents": 606,
   "PassPercentage": 97.85,
   "Difficulty": "Low"
 },
 {
   "class": "MRKT 600",
   "PassingStudents": 14,
   "TotalStudents": 17,
   "PassPercentage": 82.35,
   "Difficulty": "Medium"
 },
 {
   "class": "MRKT 601",
   "PassingStudents": 16,
   "TotalStudents": 18,
   "PassPercentage": 88.89,
   "Difficulty": "Medium"
 },
 {
   "class": "MRKT 603",
   "PassingStudents": 5,
   "TotalStudents": 6,
   "PassPercentage": 83.33,
   "Difficulty": "Medium"
 },
 {
   "class": "MRKT 606",
   "PassingStudents": 10,
   "TotalStudents": 10,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "MSAF 670",
   "PassingStudents": 73,
   "TotalStudents": 73,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "MSC 640",
   "PassingStudents": 26,
   "TotalStudents": 31,
   "PassPercentage": 83.87,
   "Difficulty": "Medium"
 },
 {
   "class": "MUSC 210",
   "PassingStudents": 998,
   "TotalStudents": 1085,
   "PassPercentage": 91.98,
   "Difficulty": "Low"
 },
 {
   "class": "NPMN 660",
   "PassingStudents": 1,
   "TotalStudents": 1,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "NSCI 100",
   "PassingStudents": 232,
   "TotalStudents": 252,
   "PassPercentage": 92.06,
   "Difficulty": "Low"
 },
 {
   "class": "NSCI 101",
   "PassingStudents": 76,
   "TotalStudents": 86,
   "PassPercentage": 88.37,
   "Difficulty": "Medium"
 },
 {
   "class": "NSCI 103",
   "PassingStudents": 130,
   "TotalStudents": 144,
   "PassPercentage": 90.28,
   "Difficulty": "Low"
 },
 {
   "class": "NSCI 120",
   "PassingStudents": 157,
   "TotalStudents": 175,
   "PassPercentage": 89.71,
   "Difficulty": "Medium"
 },
 {
   "class": "NSCI 170",
   "PassingStudents": 129,
   "TotalStudents": 145,
   "PassPercentage": 88.97,
   "Difficulty": "Medium"
 },
 {
   "class": "NSCI 171",
   "PassingStudents": 73,
   "TotalStudents": 85,
   "PassPercentage": 85.88,
   "Difficulty": "Medium"
 },
 {
   "class": "NSCI 301",
   "PassingStudents": 188,
   "TotalStudents": 219,
   "PassPercentage": 85.84,
   "Difficulty": "Medium"
 },
 {
   "class": "NSCI 362",
   "PassingStudents": 1053,
   "TotalStudents": 1212,
   "PassPercentage": 86.88,
   "Difficulty": "Medium"
 },
 {
   "class": "NURS 300",
   "PassingStudents": 349,
   "TotalStudents": 366,
   "PassPercentage": 95.36,
   "Difficulty": "Low"
 },
 {
   "class": "NURS 305",
   "PassingStudents": 363,
   "TotalStudents": 375,
   "PassPercentage": 96.8,
   "Difficulty": "Low"
 },
 {
   "class": "NURS 310",
   "PassingStudents": 17,
   "TotalStudents": 19,
   "PassPercentage": 89.47,
   "Difficulty": "Medium"
 },
 {
   "class": "NURS 350",
   "PassingStudents": 293,
   "TotalStudents": 301,
   "PassPercentage": 97.34,
   "Difficulty": "Low"
 },
 {
   "class": "NURS 360",
   "PassingStudents": 416,
   "TotalStudents": 435,
   "PassPercentage": 95.63,
   "Difficulty": "Low"
 },
 {
   "class": "NURS 362",
   "PassingStudents": 563,
   "TotalStudents": 584,
   "PassPercentage": 96.4,
   "Difficulty": "Low"
 },
 {
   "class": "NURS 410",
   "PassingStudents": 286,
   "TotalStudents": 293,
   "PassPercentage": 97.61,
   "Difficulty": "Low"
 },
 {
   "class": "NURS 420",
   "PassingStudents": 320,
   "TotalStudents": 325,
   "PassPercentage": 98.46,
   "Difficulty": "Low"
 },
 {
   "class": "NURS 460",
   "PassingStudents": 23,
   "TotalStudents": 24,
   "PassPercentage": 95.83,
   "Difficulty": "Low"
 },
 {
   "class": "NURS 462",
   "PassingStudents": 288,
   "TotalStudents": 296,
   "PassPercentage": 97.3,
   "Difficulty": "Low"
 },
 {
   "class": "NURS 485",
   "PassingStudents": 296,
   "TotalStudents": 304,
   "PassPercentage": 97.37,
   "Difficulty": "Low"
 },
 {
   "class": "NURS 498",
   "PassingStudents": 2,
   "TotalStudents": 2,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "NUTR 100",
   "PassingStudents": 29936,
   "TotalStudents": 33389,
   "PassPercentage": 89.66,
   "Difficulty": "Medium"
 },
 {
   "class": "NUTR 101",
   "PassingStudents": 2625,
   "TotalStudents": 2911,
   "PassPercentage": 90.18,
   "Difficulty": "Low"
 },
 {
   "class": "OMDE 603",
   "PassingStudents": 9,
   "TotalStudents": 9,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "OMDE 610",
   "PassingStudents": 11,
   "TotalStudents": 12,
   "PassPercentage": 91.67,
   "Difficulty": "Low"
 },
 {
   "class": "OMDE 670",
   "PassingStudents": 29,
   "TotalStudents": 30,
   "PassPercentage": 96.67,
   "Difficulty": "Low"
 },
 {
   "class": "PACE 100",
   "PassingStudents": 7292,
   "TotalStudents": 7348,
   "PassPercentage": 99.24,
   "Difficulty": "Low"
 },
 {
   "class": "PACE 111B",
   "PassingStudents": 6373,
   "TotalStudents": 7690,
   "PassPercentage": 82.87,
   "Difficulty": "Medium"
 },
 {
   "class": "PACE 111C",
   "PassingStudents": 1496,
   "TotalStudents": 1869,
   "PassPercentage": 80.04,
   "Difficulty": "Medium"
 },
 {
   "class": "PACE 111M",
   "PassingStudents": 4332,
   "TotalStudents": 4909,
   "PassPercentage": 88.25,
   "Difficulty": "Medium"
 },
 {
   "class": "PACE 111P",
   "PassingStudents": 1689,
   "TotalStudents": 2043,
   "PassPercentage": 82.67,
   "Difficulty": "Medium"
 },
 {
   "class": "PACE 111S",
   "PassingStudents": 3761,
   "TotalStudents": 4541,
   "PassPercentage": 82.82,
   "Difficulty": "Medium"
 },
 {
   "class": "PACE 111T",
   "PassingStudents": 8587,
   "TotalStudents": 9925,
   "PassPercentage": 86.52,
   "Difficulty": "Medium"
 },
 {
   "class": "PHIL 100",
   "PassingStudents": 865,
   "TotalStudents": 1086,
   "PassPercentage": 79.65,
   "Difficulty": "High"
 },
 {
   "class": "PHIL 110",
   "PassingStudents": 227,
   "TotalStudents": 295,
   "PassPercentage": 76.95,
   "Difficulty": "High"
 },
 {
   "class": "PHIL 140",
   "PassingStudents": 463,
   "TotalStudents": 565,
   "PassPercentage": 81.95,
   "Difficulty": "Medium"
 },
 {
   "class": "PHIL 304",
   "PassingStudents": 221,
   "TotalStudents": 245,
   "PassPercentage": 90.2,
   "Difficulty": "Low"
 },
 {
   "class": "PHIL 336",
   "PassingStudents": 142,
   "TotalStudents": 187,
   "PassPercentage": 75.94,
   "Difficulty": "High"
 },
 {
   "class": "PHIL 346",
   "PassingStudents": 9,
   "TotalStudents": 9,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "PHIL 348",
   "PassingStudents": 227,
   "TotalStudents": 313,
   "PassPercentage": 72.52,
   "Difficulty": "High"
 },
 {
   "class": "PHIL 349",
   "PassingStudents": 99,
   "TotalStudents": 128,
   "PassPercentage": 77.34,
   "Difficulty": "High"
 },
 {
   "class": "PHYS 122",
   "PassingStudents": 29,
   "TotalStudents": 30,
   "PassPercentage": 96.67,
   "Difficulty": "Low"
 },
 {
   "class": "PLSH 111",
   "PassingStudents": 9,
   "TotalStudents": 12,
   "PassPercentage": 75,
   "Difficulty": "High"
 },
 {
   "class": "PMAN 634",
   "PassingStudents": 301,
   "TotalStudents": 322,
   "PassPercentage": 93.48,
   "Difficulty": "Low"
 },
 {
   "class": "PMAN 637",
   "PassingStudents": 141,
   "TotalStudents": 143,
   "PassPercentage": 98.6,
   "Difficulty": "Low"
 },
 {
   "class": "PORT 111",
   "PassingStudents": 2,
   "TotalStudents": 2,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "PORT 112",
   "PassingStudents": 1,
   "TotalStudents": 1,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "PRO 600",
   "PassingStudents": 10,
   "TotalStudents": 10,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "PRPA 601",
   "PassingStudents": 6,
   "TotalStudents": 6,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "PSAD 302",
   "PassingStudents": 189,
   "TotalStudents": 202,
   "PassPercentage": 93.56,
   "Difficulty": "Low"
 },
 {
   "class": "PSAD 304",
   "PassingStudents": 321,
   "TotalStudents": 341,
   "PassPercentage": 94.13,
   "Difficulty": "Low"
 },
 {
   "class": "PSAD 306",
   "PassingStudents": 107,
   "TotalStudents": 117,
   "PassPercentage": 91.45,
   "Difficulty": "Low"
 },
 {
   "class": "PSAD 408",
   "PassingStudents": 118,
   "TotalStudents": 122,
   "PassPercentage": 96.72,
   "Difficulty": "Low"
 },
 {
   "class": "PSAD 410",
   "PassingStudents": 363,
   "TotalStudents": 380,
   "PassPercentage": 95.53,
   "Difficulty": "Low"
 },
 {
   "class": "PSAD 414",
   "PassingStudents": 344,
   "TotalStudents": 353,
   "PassPercentage": 97.45,
   "Difficulty": "Low"
 },
 {
   "class": "PSAD 416",
   "PassingStudents": 349,
   "TotalStudents": 354,
   "PassPercentage": 98.59,
   "Difficulty": "Low"
 },
 {
   "class": "PSAD 495",
   "PassingStudents": 83,
   "TotalStudents": 86,
   "PassPercentage": 96.51,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 100",
   "PassingStudents": 6405,
   "TotalStudents": 7475,
   "PassPercentage": 85.69,
   "Difficulty": "Medium"
 },
 {
   "class": "PSYC 220",
   "PassingStudents": 1447,
   "TotalStudents": 1588,
   "PassPercentage": 91.12,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 251",
   "PassingStudents": 416,
   "TotalStudents": 443,
   "PassPercentage": 93.91,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 300",
   "PassingStudents": 1852,
   "TotalStudents": 2055,
   "PassPercentage": 90.12,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 301",
   "PassingStudents": 2607,
   "TotalStudents": 2946,
   "PassPercentage": 88.49,
   "Difficulty": "Medium"
 },
 {
   "class": "PSYC 307H",
   "PassingStudents": 75,
   "TotalStudents": 78,
   "PassPercentage": 96.15,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 309BP",
   "PassingStudents": 16,
   "TotalStudents": 17,
   "PassPercentage": 94.12,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 309KL",
   "PassingStudents": 5,
   "TotalStudents": 5,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 309O",
   "PassingStudents": 6,
   "TotalStudents": 7,
   "PassPercentage": 85.71,
   "Difficulty": "Medium"
 },
 {
   "class": "PSYC 309VG",
   "PassingStudents": 23,
   "TotalStudents": 23,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 310",
   "PassingStudents": 673,
   "TotalStudents": 728,
   "PassPercentage": 92.45,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 321",
   "PassingStudents": 1299,
   "TotalStudents": 1462,
   "PassPercentage": 88.85,
   "Difficulty": "Medium"
 },
 {
   "class": "PSYC 332",
   "PassingStudents": 799,
   "TotalStudents": 842,
   "PassPercentage": 94.89,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 334",
   "PassingStudents": 43,
   "TotalStudents": 50,
   "PassPercentage": 86,
   "Difficulty": "Medium"
 },
 {
   "class": "PSYC 335",
   "PassingStudents": 1656,
   "TotalStudents": 1865,
   "PassPercentage": 88.79,
   "Difficulty": "Medium"
 },
 {
   "class": "PSYC 338",
   "PassingStudents": 578,
   "TotalStudents": 641,
   "PassPercentage": 90.17,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 341",
   "PassingStudents": 711,
   "TotalStudents": 738,
   "PassPercentage": 96.34,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 351",
   "PassingStudents": 291,
   "TotalStudents": 313,
   "PassPercentage": 92.97,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 353",
   "PassingStudents": 1406,
   "TotalStudents": 1556,
   "PassPercentage": 90.36,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 354",
   "PassingStudents": 432,
   "TotalStudents": 464,
   "PassPercentage": 93.1,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 386",
   "PassingStudents": 1503,
   "TotalStudents": 1590,
   "PassPercentage": 94.53,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 432",
   "PassingStudents": 491,
   "TotalStudents": 518,
   "PassPercentage": 94.79,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 436",
   "PassingStudents": 1354,
   "TotalStudents": 1435,
   "PassPercentage": 94.36,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 437",
   "PassingStudents": 772,
   "TotalStudents": 840,
   "PassPercentage": 91.9,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 486B",
   "PassingStudents": 4,
   "TotalStudents": 4,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 495",
   "PassingStudents": 1284,
   "TotalStudents": 1338,
   "PassPercentage": 95.96,
   "Difficulty": "Low"
 },
 {
   "class": "PSYC 836",
   "PassingStudents": 21,
   "TotalStudents": 21,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "RMBA 650",
   "PassingStudents": 14,
   "TotalStudents": 14,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "SCED 450",
   "PassingStudents": 7,
   "TotalStudents": 7,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "SCED 451",
   "PassingStudents": 8,
   "TotalStudents": 8,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "SDEV 300",
   "PassingStudents": 1621,
   "TotalStudents": 1749,
   "PassPercentage": 92.68,
   "Difficulty": "Low"
 },
 {
   "class": "SDEV 325",
   "PassingStudents": 501,
   "TotalStudents": 540,
   "PassPercentage": 92.78,
   "Difficulty": "Low"
 },
 {
   "class": "SDEV 350",
   "PassingStudents": 315,
   "TotalStudents": 355,
   "PassPercentage": 88.73,
   "Difficulty": "Medium"
 },
 {
   "class": "SDEV 360",
   "PassingStudents": 473,
   "TotalStudents": 519,
   "PassPercentage": 91.14,
   "Difficulty": "Low"
 },
 {
   "class": "SDEV 400",
   "PassingStudents": 474,
   "TotalStudents": 507,
   "PassPercentage": 93.49,
   "Difficulty": "Low"
 },
 {
   "class": "SDEV 425",
   "PassingStudents": 233,
   "TotalStudents": 239,
   "PassPercentage": 97.49,
   "Difficulty": "Low"
 },
 {
   "class": "SDEV 460",
   "PassingStudents": 398,
   "TotalStudents": 413,
   "PassPercentage": 96.37,
   "Difficulty": "Low"
 },
 {
   "class": "SOCY 100",
   "PassingStudents": 2274,
   "TotalStudents": 2460,
   "PassPercentage": 92.44,
   "Difficulty": "Low"
 },
 {
   "class": "SOCY 105",
   "PassingStudents": 42,
   "TotalStudents": 47,
   "PassPercentage": 89.36,
   "Difficulty": "Medium"
 },
 {
   "class": "SOCY 252",
   "PassingStudents": 10,
   "TotalStudents": 11,
   "PassPercentage": 90.91,
   "Difficulty": "Low"
 },
 {
   "class": "SOCY 300",
   "PassingStudents": 323,
   "TotalStudents": 352,
   "PassPercentage": 91.76,
   "Difficulty": "Low"
 },
 {
   "class": "SOCY 312",
   "PassingStudents": 15,
   "TotalStudents": 16,
   "PassPercentage": 93.75,
   "Difficulty": "Low"
 },
 {
   "class": "SOCY 313",
   "PassingStudents": 560,
   "TotalStudents": 605,
   "PassPercentage": 92.56,
   "Difficulty": "Low"
 },
 {
   "class": "SOCY 325",
   "PassingStudents": 248,
   "TotalStudents": 260,
   "PassPercentage": 95.38,
   "Difficulty": "Low"
 },
 {
   "class": "SOCY 350",
   "PassingStudents": 151,
   "TotalStudents": 161,
   "PassPercentage": 93.79,
   "Difficulty": "Low"
 },
 {
   "class": "SOCY 423",
   "PassingStudents": 136,
   "TotalStudents": 142,
   "PassPercentage": 95.77,
   "Difficulty": "Low"
 },
 {
   "class": "SOCY 426",
   "PassingStudents": 91,
   "TotalStudents": 93,
   "PassPercentage": 97.85,
   "Difficulty": "Low"
 },
 {
   "class": "SOCY 443",
   "PassingStudents": 182,
   "TotalStudents": 198,
   "PassPercentage": 91.92,
   "Difficulty": "Low"
 },
 {
   "class": "SOCY 462",
   "PassingStudents": 63,
   "TotalStudents": 68,
   "PassPercentage": 92.65,
   "Difficulty": "Low"
 },
 {
   "class": "SOCY 473",
   "PassingStudents": 34,
   "TotalStudents": 34,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "SPAN 111",
   "PassingStudents": 1299,
   "TotalStudents": 1637,
   "PassPercentage": 79.35,
   "Difficulty": "High"
 },
 {
   "class": "SPAN 112",
   "PassingStudents": 261,
   "TotalStudents": 299,
   "PassPercentage": 87.29,
   "Difficulty": "Medium"
 },
 {
   "class": "SPAN 211",
   "PassingStudents": 99,
   "TotalStudents": 114,
   "PassPercentage": 86.84,
   "Difficulty": "Medium"
 },
 {
   "class": "SPAN 212",
   "PassingStudents": 55,
   "TotalStudents": 60,
   "PassPercentage": 91.67,
   "Difficulty": "Low"
 },
 {
   "class": "SPAN 311",
   "PassingStudents": 43,
   "TotalStudents": 44,
   "PassPercentage": 97.73,
   "Difficulty": "Low"
 },
 {
   "class": "SPAN 314",
   "PassingStudents": 43,
   "TotalStudents": 48,
   "PassPercentage": 89.58,
   "Difficulty": "Medium"
 },
 {
   "class": "SPAN 418",
   "PassingStudents": 28,
   "TotalStudents": 30,
   "PassPercentage": 93.33,
   "Difficulty": "Low"
 },
 {
   "class": "SPAN 419",
   "PassingStudents": 7,
   "TotalStudents": 10,
   "PassPercentage": 70,
   "Difficulty": "High"
 },
 {
   "class": "SPCH 100",
   "PassingStudents": 8085,
   "TotalStudents": 9225,
   "PassPercentage": 87.64,
   "Difficulty": "Medium"
 },
 {
   "class": "SPCH 100X",
   "PassingStudents": 57,
   "TotalStudents": 59,
   "PassPercentage": 96.61,
   "Difficulty": "Low"
 },
 {
   "class": "SPCH 125",
   "PassingStudents": 684,
   "TotalStudents": 787,
   "PassPercentage": 86.91,
   "Difficulty": "Medium"
 },
 {
   "class": "SPCH 324",
   "PassingStudents": 474,
   "TotalStudents": 529,
   "PassPercentage": 89.6,
   "Difficulty": "Medium"
 },
 {
   "class": "SPCH 470",
   "PassingStudents": 342,
   "TotalStudents": 380,
   "PassPercentage": 90,
   "Difficulty": "Low"
 },
 {
   "class": "SPCH 472",
   "PassingStudents": 81,
   "TotalStudents": 87,
   "PassPercentage": 93.1,
   "Difficulty": "Low"
 },
 {
   "class": "SPCH 482",
   "PassingStudents": 112,
   "TotalStudents": 121,
   "PassPercentage": 92.56,
   "Difficulty": "Low"
 },
 {
   "class": "STAT 200",
   "PassingStudents": 13483,
   "TotalStudents": 16151,
   "PassPercentage": 83.48,
   "Difficulty": "Medium"
 },
 {
   "class": "STAT 225",
   "PassingStudents": 82,
   "TotalStudents": 104,
   "PassPercentage": 78.85,
   "Difficulty": "High"
 },
 {
   "class": "STAT 230",
   "PassingStudents": 98,
   "TotalStudents": 117,
   "PassPercentage": 83.76,
   "Difficulty": "Medium"
 },
 {
   "class": "STAT 400",
   "PassingStudents": 75,
   "TotalStudents": 76,
   "PassPercentage": 98.68,
   "Difficulty": "Low"
 },
 {
   "class": "SWEN 646",
   "PassingStudents": 41,
   "TotalStudents": 49,
   "PassPercentage": 83.67,
   "Difficulty": "Medium"
 },
 {
   "class": "SWEN 647",
   "PassingStudents": 65,
   "TotalStudents": 68,
   "PassPercentage": 95.59,
   "Difficulty": "Low"
 },
 {
   "class": "SWEN 651",
   "PassingStudents": 25,
   "TotalStudents": 26,
   "PassPercentage": 96.15,
   "Difficulty": "Low"
 },
 {
   "class": "SWEN 656",
   "PassingStudents": 1,
   "TotalStudents": 1,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "SWEN 670",
   "PassingStudents": 88,
   "TotalStudents": 88,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "SYSE 640",
   "PassingStudents": 11,
   "TotalStudents": 11,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "THET 110",
   "PassingStudents": 23,
   "TotalStudents": 28,
   "PassPercentage": 82.14,
   "Difficulty": "Medium"
 },
 {
   "class": "TLMN 623",
   "PassingStudents": 20,
   "TotalStudents": 22,
   "PassPercentage": 90.91,
   "Difficulty": "Low"
 },
 {
   "class": "TLMN 630",
   "PassingStudents": 32,
   "TotalStudents": 32,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "TLMN 645",
   "PassingStudents": 97,
   "TotalStudents": 97,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "TLMN 670",
   "PassingStudents": 85,
   "TotalStudents": 85,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "TMAN 625",
   "PassingStudents": 11,
   "TotalStudents": 12,
   "PassPercentage": 91.67,
   "Difficulty": "Low"
 },
 {
   "class": "TURK 111",
   "PassingStudents": 15,
   "TotalStudents": 15,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "UCSP 198B",
   "PassingStudents": 10,
   "TotalStudents": 11,
   "PassPercentage": 90.91,
   "Difficulty": "Low"
 },
 {
   "class": "UCSP 615",
   "PassingStudents": 2505,
   "TotalStudents": 2773,
   "PassPercentage": 90.34,
   "Difficulty": "Low"
 },
 {
   "class": "UCSP 615A",
   "PassingStudents": 84,
   "TotalStudents": 90,
   "PassPercentage": 93.33,
   "Difficulty": "Low"
 },
 {
   "class": "UCSP 635",
   "PassingStudents": 86,
   "TotalStudents": 98,
   "PassPercentage": 87.76,
   "Difficulty": "Medium"
 },
 {
   "class": "UCSP 636",
   "PassingStudents": 50,
   "TotalStudents": 64,
   "PassPercentage": 78.13,
   "Difficulty": "High"
 },
 {
   "class": "UMEI 020",
   "PassingStudents": 53,
   "TotalStudents": 53,
   "PassPercentage": 100,
   "Difficulty": "Low"
 },
 {
   "class": "UMEI 030",
   "PassingStudents": 58,
   "TotalStudents": 59,
   "PassPercentage": 98.31,
   "Difficulty": "Low"
 },
 {
   "class": "WMST 200",
   "PassingStudents": 751,
   "TotalStudents": 818,
   "PassPercentage": 91.81,
   "Difficulty": "Low"
 },
 {
   "class": "WRTG 101",
   "PassingStudents": 646,
   "TotalStudents": 782,
   "PassPercentage": 82.61,
   "Difficulty": "Medium"
 },
 {
   "class": "WRTG 101S",
   "PassingStudents": 1049,
   "TotalStudents": 1211,
   "PassPercentage": 86.62,
   "Difficulty": "Medium"
 },
 {
   "class": "WRTG 111",
   "PassingStudents": 18101,
   "TotalStudents": 21943,
   "PassPercentage": 82.49,
   "Difficulty": "Medium"
 },
 {
   "class": "WRTG 111X",
   "PassingStudents": 168,
   "TotalStudents": 173,
   "PassPercentage": 97.11,
   "Difficulty": "Low"
 },
 {
   "class": "WRTG 112",
   "PassingStudents": 11051,
   "TotalStudents": 13037,
   "PassPercentage": 84.77,
   "Difficulty": "Medium"
 },
 {
   "class": "WRTG 112X",
   "PassingStudents": 123,
   "TotalStudents": 131,
   "PassPercentage": 93.89,
   "Difficulty": "Low"
 },
 {
   "class": "WRTG 291",
   "PassingStudents": 169,
   "TotalStudents": 211,
   "PassPercentage": 80.09,
   "Difficulty": "Medium"
 },
 {
   "class": "WRTG 293",
   "PassingStudents": 739,
   "TotalStudents": 829,
   "PassPercentage": 89.14,
   "Difficulty": "Medium"
 },
 {
   "class": "WRTG 391",
   "PassingStudents": 4328,
   "TotalStudents": 5049,
   "PassPercentage": 85.72,
   "Difficulty": "Medium"
 },
 {
   "class": "WRTG 393",
   "PassingStudents": 6822,
   "TotalStudents": 7594,
   "PassPercentage": 89.83,
   "Difficulty": "Medium"
 },
 {
   "class": "WRTG 394",
   "PassingStudents": 5599,
   "TotalStudents": 6258,
   "PassPercentage": 89.47,
   "Difficulty": "Medium"
 },
 {
   "class": "WRTG 490",
   "PassingStudents": 74,
   "TotalStudents": 80,
   "PassPercentage": 92.5,
   "Difficulty": "Low"
 }
]

################################################################
# create Course Difficulty table

drop_table('course_difficulty', c)
c.execute('''
    CREATE TABLE course_difficulty (
        id INTEGER PRIMARY KEY,
        course TEXT,
        total_students INTEGER,
        passing_students INTEGER,
        pass_percentage FLOAT,
        difficulty TEXT
    )
''')

c.executemany('''
    INSERT INTO course_difficulty (
            course, total_students, passing_students, pass_percentage, difficulty) 
        VALUES (:class, :TotalStudents, :PassingStudents, :PassPercentage, :Difficulty)
''', difficulty)

conn.commit()

# Close the connection
conn.close()

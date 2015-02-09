# -*- coding: utf-8 -*-

class DefaultConfig:
  DEBUG = False

  PORT_RETRIES = 50
  SETTINGS = {
    "NUMCHAR": 200,
    "MAXZOOM": 100,
    "LOADCHAR": 200 * 100,
    "DOWNSAMPLE": 50,
  }

  BAM = None
  BAMDIR = None
  REFFILE = None
  TARGETFILE = None

  BAMFILE_TO_BAMVIEW = {}
  TARGET_LIST = []

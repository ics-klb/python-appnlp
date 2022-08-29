# -*- coding: utf-8 -*-
"""
Default ChatNlp settings for Content.
"""
from botnlp.storage.extend import settings


CHATNLP_SETTINGS = getattr(settings, 'CHATNLP', {})

CHATNLP_DEFAULTS = {
    'name': 'CHATNLP',
    'storage_adapter': 'CHATNLP.storage.TextStorageAdapter'
}

CHATNLP = CHATNLP_DEFAULTS.copy()
CHATNLP.update(CHATNLP_SETTINGS)

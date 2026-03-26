from sampletool.key_parser import extract_bpm, extract_key, parse_filename, build_filename, ParseResult


# --- BPM ---

def test_bpm_standard():
    bpm, clean = extract_bpm("Bass_Loop_140_Dm")
    assert bpm == "140"
    assert "140" not in clean

def test_bpm_none():
    bpm, clean = extract_bpm("Bass_Loop_Dm")
    assert bpm is None
    assert clean == "Bass_Loop_Dm"

def test_bpm_not_in_longer_number():
    bpm, _ = extract_bpm("Sample1401")
    assert bpm is None

def test_reject_bpm_below_60():
    bpm, _ = extract_bpm("Bass_Loop_59_Dm")
    assert bpm is None

def test_reject_bpm_above_239():
    bpm, _ = extract_bpm("Bass_Loop_240_Dm")
    assert bpm is None


# --- Tonalité ---

def test_key_minor_simple():
    key, warning, _ = extract_key("Bass_Am_Loop")
    assert key == "Am"
    assert warning is False

def test_key_minor_sharp():
    key, warning, _ = extract_key("Lead_C#m_Arp")
    assert key == "C#m"
    assert warning is False

def test_key_minor_flat():
    key, warning, _ = extract_key("Pad_Bbmin_Soft")
    assert key == "Bbmin"
    assert warning is False

def test_key_major_explicit():
    key, warning, _ = extract_key("Rhodes_Cmaj_Chord")
    assert key == "Cmaj"
    assert warning is False

def test_key_camelot():
    key, warning, _ = extract_key("Loop_7A_Deep")
    assert key == "7A"
    assert warning is False

def test_key_major_implicit_warning():
    key, warning, _ = extract_key("Bass_A_Loop")
    assert key == "A"
    assert warning is True

def test_key_none():
    key, warning, _ = extract_key("Kick_Hard_Loop")
    assert key is None
    assert warning is False


# --- Parse complet ---

def test_parse_full():
    result = parse_filename("SHADOW_BASS_140_Am_Loop")
    assert result.bpm == "140"
    assert result.key == "Am"
    assert result.key_warning is False
    assert "140" not in result.clean_stem
    assert "Am" not in result.clean_stem

def test_build_filename_full():
    result = ParseResult(bpm="140", key="Am", key_warning=False, clean_stem="Bass_Loop")
    assert build_filename(result, ".wav") == "140_Am_Bass_Loop.wav"

def test_build_filename_no_key():
    result = ParseResult(bpm="128", key=None, key_warning=False, clean_stem="Kick")
    assert build_filename(result, ".wav") == "128_Kick.wav"

def test_build_filename_no_bpm():
    result = ParseResult(bpm=None, key="Dm", key_warning=False, clean_stem="Pad_Soft")
    assert build_filename(result, ".wav") == "Dm_Pad_Soft.wav"

def test_key_parentheses():
    key, warning, clean = extract_key("KSHMR_Sitar_Hypnotic_Ambiance_01_(C)")
    assert key == "C"
    assert warning is False

def test_key_parentheses_sharp():
    key, warning, clean = extract_key("KSHMR_Sitar_(F#)_loop")
    assert key == "F#"
    assert warning is False

def test_key_major_implicit_not_at_start():
    # 'A' en début de nom → ignoré
    key, warning, _ = extract_key("A good whoosh boom")
    assert key is None

def test_key_major_implicit_at_end():
    # 'D' en fin de nom isolé → détecté avec warning
    key, warning, _ = extract_key("BD_174_D")
    assert key == "D"
    assert warning is True

def test_key_minor_not_at_start():
    # 'Am' en début → ignoré
    key, _, _ = extract_key("Am loop bass")
    assert key is None

def test_key_minor_in_middle():
    # 'Am' en milieu → détecté
    key, _, _ = extract_key("Bass_Am_Loop")
    assert key == "Am"

def test_bpm_word_removed():
    bpm, clean = extract_bpm("bCloop1_112bpm")
    assert bpm == "112"
    assert "bpm" not in clean.lower()

def test_bpm_leading_zero_ignored():
    bpm, _ = extract_bpm("060_One_Shot_D#")
    assert bpm is None

def test_bpm_no_leading_zero():
    bpm, _ = extract_bpm("150_bass_tonal")
    assert bpm == "150"
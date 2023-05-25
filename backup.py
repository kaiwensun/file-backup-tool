from translations import text as t, EN, ZH
from functools import cache
from collections import defaultdict
import os, datetime, sys, collections, shutil, argparse


NEW_ENTRY_TOKEN = "+"
prefix = []
PRINT_WIDTH = 2
DRY_RUN = False
assert PRINT_WIDTH >= 2

DfsPair = collections.namedtuple('DfsPair', ['src', 'dst'])

class PseudoDirEntry:
    def __init__(self, path):
        self._path = os.path.abspath(path)
        assert os.path.exists(self.path)
    @property
    def path(self):
        return self._path
    @property
    def name(self):
        return os.path.basename(self.path)
    def is_dir(self, follow_symlinks=True):
        return os.path.isdir(self._real_path if follow_symlinks else self.path)
    def is_file(self, follow_symlinks=True):
        return os.path.isfile(self._real_path if follow_symlinks else self.path)
    def is_symlink(self):
        return os.path.islink(self.path)
    def stat(self):
        return os.stat(self.path, follow_symlinks=False)
    @property
    def _real_path(self):
        return os.path.realpath(self.path)

def tr(text, **kwargs):
    return t(text, ZH, **kwargs)

def print_regular(text, end="\n"):
    if end == "" and not text.endswith(" "):
        text += " "
    left = (" " * PRINT_WIDTH + "|") * (len(prefix) - 1) + " " * PRINT_WIDTH
    print(left + text, end=end)

def print_new_entry():
    # the new entry should have been already pushed to `prefix`
    if len(prefix) > 1:
        print_empty_line()
        left = (" " * PRINT_WIDTH + "|") * (len(prefix) - 1)
        print(left[:-1] + NEW_ENTRY_TOKEN + "-" * (PRINT_WIDTH - 1) + prefix[-1].src.name)
    else:
        print(f"[{tr('backup root')}]")

def print_empty_line():
    left = (" " * PRINT_WIDTH + "|") * (len(prefix) - 1)
    print(left)

def get_input(available_options={}, begin_line=True):
    assert 'q' not in available_options
    if not available_options:
        available_options = {
            "y": tr("Yes"),
            "n": tr("No")
        }
    available_options = {**available_options, "q": tr("Quit")}
    value = None
    left = (" " * PRINT_WIDTH + "|") * len(prefix) + " " * PRINT_WIDTH if begin_line else ""
    prompt = left + ", ".join(f"[{key}] {desc}" for key, desc in available_options.items()) + ": "
    while value not in available_options:
        value = input(prompt)
        left = (" " * PRINT_WIDTH + "|") * len(prefix) + " " * PRINT_WIDTH
        prompt = left + ", ".join(f"[{key}] {desc}" for key, desc in available_options.items()) + ": "
    if value == "q":
        print(tr("Quitting..."))
        sys.exit(0)
    return value

def get_roots():
    def validate(path):
        if not os.path.exists(path):
            print(f"{tr('Folder not found: ')}{path}")
            return False
        if not os.path.isdir(path):
            print(f"{tr('Not a folder: ')}{path}")
            return False
        return True

    parser = argparse.ArgumentParser(description=tr("bakckup tool"))
    parser.add_argument('-s', '--src', help=tr('source path'))
    parser.add_argument('-d', '--dst', help=tr('destination path'))
    parser.add_argument('--dry-run', action='store_true', help=tr("Do not actually move or copy any files"))

    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(1)

    if args.dry_run:
        global DRY_RUN
        print(tr("Running in dry-run mode"))
        DRY_RUN = True
    src = args.src or input(tr("What's the path of the source folder?"))
    while not validate(src):
        src = input(tr("What's the path of the source folder?"))
    dst = args.dst or input(tr("What's the path of the destination folder?"))
    while not validate(dst):
        dst = input(tr("What's the path of the destination folder?"))
    prefix.append(DfsPair(
        PseudoDirEntry(src),
        PseudoDirEntry(dst)
    ))

def copy_entry(entry):
    src_path = os.path.join(prefix[-1].src.path, entry.name)
    dst_path = os.path.join(prefix[-1].dst.path, entry.name)
    if os.path.exists(dst_path):
        raise Exception(f"{dst_path} already exists")

    if entry.is_dir(follow_symlinks=False):
        if DRY_RUN:
            print_regular(f"{tr('[DRYRUN]')} shutil.copytree({src_path}, {dst_path})")
        else:
            shutil.copytree(src_path, dst_path)
    else:
        if DRY_RUN:
            print_regular(f"{tr('[DRYRUN]')} shutil.copy2({src_path}, {dst_path})")
        else:
            shutil.copy2(src_path, dst_path)

def replace_entry():
    src_path = prefix[-1].src.path
    dst_path = prefix[-1].dst.path
    if not os.path.exists(dst_path):
        raise Exception(f"{dst_path} doesn't exists. Why are you replacing?")
    if prefix[-1].src.is_dir() or prefix[-1].dst.is_dir():
        raise Exception("entry replacement can't deal with folders")
    if DRY_RUN:
        print_regular(f"{tr('[DRYRUN]')} shutil.copy2({src_path}, {dst_path})")
    else:
        shutil.copy2(src_path, dst_path)

    
def get_entry_datetime(entry, mode='m'):
    if mode == 'c':
        timestamp = entry.stat().st_ctime
    elif mode == 'm':
        timestamp = entry.stat().st_mtime
    else:
        raise Exception(f"unknown mode {mode}")
    return datetime.datetime.fromtimestamp(timestamp)

def datetime2str(datetime):
    fmt = "%Y-%m-%d %H:%M:%S"
    return datetime.strftime(fmt)

def get_file_entry_type_string(entry):
    if entry.is_symlink():
        typ = "symlink"
    elif entry.is_dir(follow_symlinks=False):
        typ = "folder"
    elif entry.is_file(follow_symlinks=False):
        typ = "file"
    else:
        raise Exception(f"Unknown type entry {entry}")
    return tr(typ)

def entry_short_type(entry):
    if entry.is_symlink():
        typ = "L"
    elif entry.is_dir(follow_symlinks=False):
        typ = "D"
    elif entry.is_file(follow_symlinks=False):
        typ = "F"
    else:
        raise Exception(f"Unknown type entry {entry}")
    return typ

def add_to_trie(trie, suffix):
    p = trie
    for c in reversed(suffix):
        p = p[c]
    p[None] = True

def is_in_trie(trie, suffix):
    p = trie
    for c in reversed(suffix):
        p = p.get(c)
        if not p:
            return False
        if p.get(None):
            return True
    return False

@cache
def get_skips(file_name):
    file_path = os.path.join(os.path.dirname(sys.argv[0]), file_name)
    Trie = lambda: defaultdict(Trie)
    trie = Trie()
    if not os.path.exists(file_path):
        open(file_path, "a").close()
    if not os.path.isfile(file_path):
        raise Exception(f"{file_path} is not a file")
    with open(file_path, "r", encoding='UTF-8') as f:
        for line in f.readlines():
            line = line.strip()
            if line and not line.startswith("#"):
                add_to_trie(trie, line)
    return trie

def quick_compare(src_entries, dst_entries):
    extra_src = []
    extra_dst = []
    i = j = 0
    while i < len(src_entries) or j < len(dst_entries):
        s = src_entries[i] if i < len(src_entries) else None
        d = dst_entries[j] if j < len(dst_entries) else None
        if s is None:
            if not is_in_trie(get_skips("skip_dst.txt"), d.path):
                extra_dst.append(d)
            j += 1
            continue
        if d is None:
            if not is_in_trie(get_skips("skip_src.txt"), s.path):
                extra_src.append(s)
            i += 1
            continue
        if s.name == d.name:
            i += 1
            j += 1
            continue
        elif s.name < d.name:
            if not is_in_trie(get_skips("skip_src.txt"), s.path):
                extra_src.append(s)
            i += 1
        else:
            if not is_in_trie(get_skips("skip_dst.txt"), d.path):
                extra_dst.append(d)
            j += 1
    if extra_src:
        print_empty_line()
        print_regular(tr("Source has the following more items in this folder"))
        for extra in extra_src:
            print_regular(f"  [{entry_short_type(extra)}] {extra.name}")
    if extra_dst:
        print_empty_line()
        print_regular(tr("Destination has the following more items in this folder"))
        for extra in extra_dst:
            print_regular(f"  [{entry_short_type(extra)}] {extra.name}")
    if extra_dst:
        print_regular(tr("Please acknowledge the diff"))
        get_input({"a": tr("Acknowledge")})
    if extra_src:
        print_regular(tr("Would you like to copy all the extra source files/folders to destination? "), end="")
        answer = get_input({
            "y": tr("Yes"),
            "n": tr("No"),
            "s": tr("Let me select")
        }, begin_line=False)
        if answer == "y":
            for extra in extra_src:
                copy_entry(extra)
        elif answer == "s":
            for extra in extra_src:
                print_regular(f"{extra.name}", end="")
                if get_input(begin_line=False) == "y":
                    copy_entry(extra)
            print_regular(tr("All processed"), end="")
    return extra_src, extra_dst

def is_folder_structure_same():
    try:
        for s, d in zip(os.walk(prefix[-1].src.path), os.walk(prefix[-1].dst.path), strict=True):
            if s[1:] != d[1:]:
                print(s, d)
                return False
    except ValueError:
        # zip exhustd one iterator before another
        return False
    return True

def walk(src, dst):
    src_entries = sorted(os.scandir(src), key=lambda f: f.name)
    dst_entries = sorted(os.scandir(dst), key=lambda f: f.name)
    quick_compare(src_entries, dst_entries)
    i = j = 0
    while i < len(src_entries) and j < len(dst_entries):
        s = src_entries[i]
        d = dst_entries[j]
        i += 1
        j += 1
        if s.name < d.name:
            j -= 1
            continue
        if s.name > d.name:
            i -= 1
            continue
        prefix.append(DfsPair(s, d))
        try:
            print_new_entry()
            if get_file_entry_type_string(s) != get_file_entry_type_string(d):
                print_regular(tr("src is {src_type}, dst is {dst_type}. Please backup manually.", src_type=tr(get_file_entry_type_string(s)), dst_type=tr(get_file_entry_type_string(d))))
                get_input({"a": tr("Acknowledge")})
                prefix.pop()
                continue
            if s.is_dir(follow_symlinks=False):
                is_repo = all(os.path.isdir(os.path.join(e.path, ".git")) for e in [s, d])
                if is_repo:
                    # If repo structures are same, then compare only file names.
                    # (assuming different folders result in different blob and tree object names.)
                    if not is_folder_structure_same():
                        print_regular(tr("Git repo {path} is different from destination. Please backup manually.", path=s.path))
                        get_input({"a": tr("Acknowledge")})
                else:
                    walk(s.path, d.path)
            else:
                src_size = s.stat().st_size
                dst_size = d.stat().st_size
                src_mtime = get_entry_datetime(s)
                dst_mtime = get_entry_datetime(d)
                is_diff = False
                entry_typ = get_file_entry_type_string(s)
                if src_size != dst_size:
                    print_regular(tr("{entry_typ} sizes of src and dst are different: {src_size}B vs {dst_size}B", entry_typ=entry_typ, src_size=src_size, dst_size=dst_size))
                    is_diff = True
                if src_mtime != dst_mtime:
                    print_regular(tr("{entry_typ} last modified time of src and dst are different: {src_time} vs {dst_time}",
                                     entry_typ=tr(entry_typ),
                                     src_time=datetime2str(src_mtime),
                                     dst_time=datetime2str(dst_mtime)
                                     ))
                    is_diff = True
                if is_diff:
                    print_regular(tr("Would you like to backup? This will override the existing backup."), end="")
                    if "y" == get_input(begin_line=False):
                        replace_entry()
        finally:
            prefix.pop()


def main():
    get_roots()
    print_new_entry()
    walk(prefix[0].src.path, prefix[0].dst.path)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import hashlib
import io
import tarfile
from pathlib import Path

import boto3
from tqdm import tqdm


def get_children(path):
    return sorted(p for p in path.glob("**/*") if p.is_file())


def get_checksum(path, use_content=False):
    children = get_children(path)
    checksum = hashlib.md5()
    for child in children:
        checksum.update(child.as_posix().encode())
        if use_content:
            with open(child, "rb") as f:
                checksum.update(f.read())
    return checksum.hexdigest()


def create_tarball(files):
    tar_data = io.BytesIO()
    for child in files:
        with tarfile.open(fileobj=tar_data, mode="w:gz") as tar:
            tar.add(child)
    tar_data.seek(0)
    return tar_data


def download_hash(bucket, key):
    outfile = io.BytesIO()
    try:
        bucket.download_fileobj(key, outfile)
        outfile.seek(0)
        return outfile.read().decode()
    except Exception:
        return None


def get_hashfile_name(item):
    return item.name + ".md5"


def get_archive_name(item):
    return item.name + ".tar.gz"


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("path", type=Path, help="path to backup")
    p.add_argument("--dryrun", action="store_true", help="dry run")
    p.add_argument("--checksum-content", action="store_true", help="checksum content")
    p.add_argument(
        "--upload-checksum-only",
        action="store_true",
        help="upload checksum only (WARNING: dangerous)",
    )
    p.add_argument("--bucket", help="bucket name", required=True)
    p.add_argument("--profile", help="aws profile name")
    p.add_argument("--storage-class", help="aws storage class", default="STANDARD")
    p.add_argument("--verbose", action="store_true", help="verbose")
    args = p.parse_args()

    session = boto3.Session(profile_name=args.profile)
    s3 = session.resource("s3")
    bucket = s3.Bucket(args.bucket)

    items = sorted(args.path.glob("*"))
    for item in tqdm(items, desc="Uploading", unit="files", total=len(items)):
        checksum = get_checksum(item, use_content=args.checksum_content)
        if args.verbose:
            tqdm.write(f"{item.name} - {checksum}")

        remote_checksum = download_hash(bucket, get_hashfile_name(item))

        if checksum != remote_checksum:
            if args.verbose:
                tqdm.write(f"{item.name} changed, uploading...")
            if not args.dryrun:
                tarball = create_tarball(get_children(item))
                if not args.upload_checksum_only:
                    bucket.upload_fileobj(
                        tarball,
                        get_archive_name(item),
                        ExtraArgs={"StorageClass": args.storage_class},
                    )
                bucket.put_object(Body=checksum, Key=get_hashfile_name(item))
        else:
            if args.verbose:
                tqdm.write(f"{item.name} unchanged, skipping...")

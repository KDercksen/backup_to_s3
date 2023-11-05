Simple backup utility to sync top level folders to an S3 bucket. Stores each
directory as a tar.gz file in the bucket, and also uploads a checksum file for
each archive.

If checksum has not changed, the archive will be skipped in the next run.

One way backup only for now, no deletion of files in the bucket and no
functionality to copy files back from the bucket (maybe I will implement this
later).

Example:

```
rootdir/
    dir1/
        file1
        file2
    dir2/
        file3
        file4
```

will be uploaded as `dir1.tar.gz` + `dir1.md5` and `dir2.tar.gz` + `dir2.md5`.

## Usage

```bash
python backup.py /path/to/dir --bucket my-bucket --profile my-aws-profile --storage-class DEEP_ARCHIVE
```

Arguments:

| Argument                 | Description                                                                                                                                                         |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `path`                   | Path to the directory to backup                                                                                                                                     |
| `--bucket`               | Name of the S3 bucket to upload to                                                                                                                                  |
| `--profile`              | AWS profile to use (optional, will use `default` when not specified)                                                                                                |
| `--storage-class`        | Storage class to use (optional, defaults to STANDARD)                                                                                                               |
| `--verbose`              | Print verbose output (optional)                                                                                                                                     |
| `--dryrun`               | Do not upload anything, just print what would be uploaded (optional)                                                                                                |
| `--checksum-content`     | Use filename plus file content to calculate checksum. If not specified, only filename is used (optional)                                                            |
| `--upload-checksum-only` | Only upload checksum files, do not upload archives (optional). WARNING: this may compromise understanding of data integrity, only use if you know what you're doing |

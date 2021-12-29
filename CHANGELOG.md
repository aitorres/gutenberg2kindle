
# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.2.0] - 2021-12-29

### Added

- You can now download more than one book in the same run instead of running the CLI several times; the `--book-id` flag now supports several IDs as input.

### Changed

- CLI flags now have a short version that can be seen with `--help`
- CLI will now request the user's SMTP password _before_ downloading the first book, and re-use the same password in case multiple book downloads were requested.

## [0.1.1] - 2021-12-17

### Added

- Support to set the desired ebook format to be downloaded from Gutenberg: Kindle with Images, Kindle without Images, or Auto.

### Changed

- The default format for ebooks is "Auto": the tool will attempt to download the book in Project Gutenberg's "Kindle with Images" format, and if not available, will fallback to "Kindle without Images".

## [0.1.0] - 2021-12-12

Initial release!

### Added

- The tool can be set up
- The tool can download a book from Project Gutenberg's website, given its ID, and send it through email.

# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.3.0] - 2022-05-23

### Changed

- The tool will now download ebooks in the `EPUB` format, instead of the `MOBI` format, since `MOBI` will be deprecated from the Send 2 Kindle function in late 2022. Read [this](https://www.amazon.com/sendtokindle/email) and [this](https://www.amazon.com/gp/help/customer/display.html?nodeId=G5WYD9SAF7PGXRNA) for more context.
- Dependency updates

## [0.2.2] - 2022-02-06

### Added

- You can config the tool interactively with the new `interactive-config` command

### Changed

- Small type hint changes and general refactoring
- Dependency upgrades

## [0.2.1] - 2021-12-30

### Fixed

- Solve a possible memory leak when sending multiple books by manually closing each book's buffer after an email has been sent.

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

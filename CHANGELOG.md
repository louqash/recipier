# CHANGELOG

<!-- version list -->

## v2.0.1 (2026-01-14)

### Bug Fixes

- Merge budyn and remove unit_size from syrop
  ([`8307e05`](https://github.com/louqash/recipier/commit/8307e05a1b68f4089da085889045c535d7b1e4a7))


## v2.0.0 (2026-01-13)

### Bug Fixes

- Remove redundant g from package size text
  ([`406af6d`](https://github.com/louqash/recipier/commit/406af6d72c01d3814833fd742290a0b4c225960d))

### Chores

- Apply black formatting
  ([`a93f579`](https://github.com/louqash/recipier/commit/a93f579528f509888c453d7b76dd40e01b22ff5e))

- Improve logging
  ([`3031ad8`](https://github.com/louqash/recipier/commit/3031ad8f148a974345aab6ec5dc013fe3bdaaaeb))

- Remove unused ingredients from the database
  ([`32d3b48`](https://github.com/louqash/recipier/commit/32d3b4800b4713d5e63fb3e18b5d2b57b6ea9c1b))

### Features

- Add ingredients to serving tasks
  ([`6edeef4`](https://github.com/louqash/recipier/commit/6edeef440a536b26b1a2f117fe037f60a6640d86))

- Add macronutients to the database and the UI
  ([`e3e7deb`](https://github.com/louqash/recipier/commit/e3e7deb80da71e419289f776b9772a3802623b54))

- Add warning banner to warn of rounding errors before task creation
  ([`edee2ac`](https://github.com/louqash/recipier/commit/edee2ac88f7186f2f75d386b2206784bbe651c3a))

- Allow for different cooking dates per person
  ([`c7bd225`](https://github.com/louqash/recipier/commit/c7bd225f48c253963c6e47ece56433736910a021))

- Make frontend use validation endpoint
  ([`bcb2cb7`](https://github.com/louqash/recipier/commit/bcb2cb7b2df71500ee9e1e54fc2790480f37fd69))

- Version 2.0.0 release
  ([`51724d4`](https://github.com/louqash/recipier/commit/51724d40640fa46062732b1183483c5b0b89379a))


## v1.8.0 (2026-01-10)

### Bug Fixes

- Fix skyr naturalny
  ([`2085862`](https://github.com/louqash/recipier/commit/2085862ae293e09a528460aa15e53b83e23cd6df))

### Chores

- Update uv.lock after version bump [skip ci]
  ([`c5d8e91`](https://github.com/louqash/recipier/commit/c5d8e91a961b5867aca80cd0c6d30f732be73d6a))

### Continuous Integration

- Run uv sync before semantic release commits
  ([`de8768f`](https://github.com/louqash/recipier/commit/de8768f761e8f3ea05f5dc023822a78f4b999b53))

### Features

- Add display units
  ([`0dbe309`](https://github.com/louqash/recipier/commit/0dbe309d39178ce43aa837011aa69c08e78b6715))


## v1.7.2 (2026-01-10)

### Bug Fixes

- Setting still not visible
  ([`9a44201`](https://github.com/louqash/recipier/commit/9a44201973fbd05f68d2eb37ba76ab23b4338bcb))

### Continuous Integration

- Run uv sync after semantic release
  ([`cb5c6bf`](https://github.com/louqash/recipier/commit/cb5c6bfdff7f8ad0f4c1c9310bdcf6e6a23880df))


## v1.7.1 (2026-01-10)

### Bug Fixes

- Make setting visible even if todoist token is there
  ([`6bad5d4`](https://github.com/louqash/recipier/commit/6bad5d48f2644e5491f0c0155c620fc58981ce17))

- Tweaks to meals database
  ([`9283cff`](https://github.com/louqash/recipier/commit/9283cff9ee92563c2da6138ee738ec2071170b9a))


## v1.7.0 (2026-01-10)

### Continuous Integration

- Add semantic release workflow
  ([`da7da6b`](https://github.com/louqash/recipier/commit/da7da6b31662b9c764570bdf06396b52cc8b10e7))

- Fix to sha docker tagging
  ([`9764b84`](https://github.com/louqash/recipier/commit/9764b8441289f3ec602036a39a9676df669785b3))

- Make release workflow trigger only on tags
  ([`8682868`](https://github.com/louqash/recipier/commit/8682868366fb4d5d257375f19b4c97b04f6c71f9))

### Features

- Add font size setting
  ([`c9e45a9`](https://github.com/louqash/recipier/commit/c9e45a99eb2ffe2701f4dc9339bb591456507f0d))

- Scale meals to around 450kcal in base portions
  ([`7d1c184`](https://github.com/louqash/recipier/commit/7d1c1847311d611e2482c6cc85e58cd226ccd610))


## v1.6.0 (2026-01-10)

### Continuous Integration

- Add github workflow to build docker image
  ([`a7b396e`](https://github.com/louqash/recipier/commit/a7b396ecf19d64c303a0e07a136cdba9c3518b35))

### Features

- Add a footer and semantic release
  ([`8620229`](https://github.com/louqash/recipier/commit/86202299e97961a32b4f216dc618c60c8c739772))


## v1.5.0 (2026-01-09)

### Features

- Add search by ingredient
  ([`02cd432`](https://github.com/louqash/recipier/commit/02cd4321dbed65cb14568a91c49af235af5eeac1))


## v1.4.0 (2026-01-10)

### Code Style

- Apply black and isort
  ([`6743964`](https://github.com/louqash/recipier/commit/67439648d98a1c4501baab9b4758c3b99bc4d8d8))

### Features

- Add ingredient rounding to package_size
  ([`ae9ab7a`](https://github.com/louqash/recipier/commit/ae9ab7a8f1a13c04fc906cf27f413e034587cbae))

### Testing

- Fix tests after config changes
  ([`239f3a7`](https://github.com/louqash/recipier/commit/239f3a74e3e704169f12d920a12985f52db32a1e))

### Breaking Changes

- Config and API changes


## v1.3.1 (2026-01-10)

### Bug Fixes

- Wrong calories in the database
  ([`cb55055`](https://github.com/louqash/recipier/commit/cb55055ca95f98f8d17d71c871a73a936a10ab35))


## v1.3.0 (2026-01-10)

### Features

- Config revamp
  ([`1bf2287`](https://github.com/louqash/recipier/commit/1bf228743ff053ae35b1131f13578950928c6b8e))

### Breaking Changes

- Config structure has changed - that means old configs won't work


## v1.2.0 (2026-01-10)

### Features

- Add MealDetailsModal with additional info about a meal
  ([`75645de`](https://github.com/louqash/recipier/commit/75645de61329a0cc72b4afef6a6b2b15c7b651c4))


## v1.1.0 (2026-01-10)

### Features

- Add cooking steps and suggested seasonings
  ([`50c0eca`](https://github.com/louqash/recipier/commit/50c0eca2b4edab23339241af9635e0740e69137e))


## v1.0.0 (2026-01-06)

### Continuous Integration

- Add github workflow
  ([`5deea66`](https://github.com/louqash/recipier/commit/5deea6682e1e2fd4ed13ed878338b076f7b8024a))

### Documentation

- Fix broken links in README
  ([`ae3ed66`](https://github.com/louqash/recipier/commit/ae3ed66ad2f25359d4fb2d7a0cbbff46c1d92536))

- Fix github username
  ([`9b7dae0`](https://github.com/louqash/recipier/commit/9b7dae00d8f2bf1b57e410e36a14dba07820524c))

### Features

- Add tests
  ([`7d3e8ab`](https://github.com/louqash/recipier/commit/7d3e8abfa77cb51ea29e301d42aaaacdc9178ffb))

- Release v1.0.0 - production ready
  ([`1d998b2`](https://github.com/louqash/recipier/commit/1d998b2334f0aa73af4b25cb7270f5f0c8b41116))


## v0.4.0 (2026-01-10)

### Features

- Bump python do 3.12+
  ([`be69f3f`](https://github.com/louqash/recipier/commit/be69f3f9c263b77b9b15ccbebdad1bb0ffde62b7))

### Refactoring

- Add black and isort
  ([`c905c54`](https://github.com/louqash/recipier/commit/c905c543a481c5e560d5d96c984e5034a24fe3c2))


## v0.3.0 (2026-01-10)

### Bug Fixes

- Bug fixes + small refactor
  ([`32a6d76`](https://github.com/louqash/recipier/commit/32a6d76aabcc5565f72db70f1412afdaf470284e))

### Chores

- Update README
  ([`2c1f10d`](https://github.com/louqash/recipier/commit/2c1f10dfbc4f066a5324f0b8e8ed7283c37c3c5f))

### Features

- Add calories of ingredients and meals
  ([`b05a686`](https://github.com/louqash/recipier/commit/b05a6866a4609fdd60c33db54f6dd65c633e2627))

- Add light/dark themes
  ([`4170f0c`](https://github.com/louqash/recipier/commit/4170f0c5b5edd074ec04a2ba8aa5dffd127b6425))

- Change number of portions to eating dates
  ([`9d00c44`](https://github.com/louqash/recipier/commit/9d00c442d2b865300042b3beb57a142eaa540137))

- Display combined calories for a day
  ([`69e25a8`](https://github.com/louqash/recipier/commit/69e25a8cac825d1102e54f7d28fd380006e73b8d))


## v0.2.0 (2026-01-10)

### Documentation

- Update README.md
  ([`e1c0c33`](https://github.com/louqash/recipier/commit/e1c0c33dc5d2c62ca000fb1f1319fddccafae3c6))

### Features

- Add generate meal plan script
  ([`af8ea7e`](https://github.com/louqash/recipier/commit/af8ea7e021748ed207ebd144994e3e3883879028))

- Add new data
  ([`8ed13f8`](https://github.com/louqash/recipier/commit/8ed13f8369863cd87a7bb5f18a57e39514155df5))

- Add task assignment to users
  ([`a35c011`](https://github.com/louqash/recipier/commit/a35c0112e95b2d219dded8c569b12888b39a0dd5))

- Make users dynamic
  ([`feb4829`](https://github.com/louqash/recipier/commit/feb482974326caba671e8059788d113a5d9a8219))

- Separate meals into database
  ([`42162d7`](https://github.com/louqash/recipier/commit/42162d7c6e6e763442e769a09e591111d9b6064e))

- Web UI
  ([`dfa5abf`](https://github.com/louqash/recipier/commit/dfa5abfc0c34fb746361292ae068a4887e870b63))


## v0.1.0 (2026-01-10)

- Initial Release

# Contributing to Gitmit

Thank you for your interest in contributing to this project. Contributions are welcome and will be fully credited. However, it is important to follow the standards outlined in this document to maintain code consistency at all times. We follow a **Git Flow** workflow to maintain a clean, stable, and collaborative codebase. Please read these guidelines carefully before creating a issue or submitting a pull request.

## Etiquette

This project is open source, and as such, its contributors generously give their free time to build and maintain the source code contained herein. They make the code freely available in the hope that it will be useful to other developers. It would be extremely unfair for them to be subjected to insults for their hard work.

Please be kind to the contributors when raising issues or submitting your pull requests. We have also taken the time to build a wiki for this library—perhaps your questions might be answered there. Let’s show the world that developers are civilized and altruistic individuals.

It is also the contributor’s duty to ensure that all submissions to the project are of sufficient quality to be beneficial. Many developers have different skill sets, strengths, and weaknesses. Please respect the contributor's decisions, and do not be upset or offended if your submission is not used.

## Viability

When requesting or submitting new features, first consider whether they might be helpful to others. Open source projects are used by many developers, who may have very different needs than you. Consider whether or not your feature might be useful to other users of the project.

## Procedure

Before filing an *issue*:

- Try to replicate the problem, to make sure it wasn't a coincidental incident;
- Make sure your feature suggestion isn't already present in the project;
- Check the pull requests tab to make sure the bug doesn't have a fix in progress;
- Also, check the pull requests tab to make sure the feature isn't already in progress.

Before submitting a *pull request*:

- Check the codebase to make sure your feature doesn't already exist;
- Check pull requests to make sure someone else hasn't submitted the feature or fix yet.

## Requirements

If the project maintainer has any additional requirements, you will find them listed here.

- **Add tests**:  Your patch won't be accepted if it doesn't have tests;
- **Document any change in behaviour**: Make sure the `README.md` and any other relevant documentation are kept up-to-date;
- **Consider our release cycle**: We try to follow [SemVer v2.0.0](https://semver.org/). Randomly breaking public APIs is not an option;
- **Workflow**: To be consistent, this project follows the workflow pattern, be sure to use it when sending any pull requests.
- **One pull request per feature**: If you want to do more than one thing, send multiple pull requests.

### Commits

We follow a strict commit message format to maintain clarity and consistency in our project's history. Every commit message should use the following format:

```txt
:type_emoji: type(scope): Title

Description
```

- **:type_emoji:** The emoji representing the type of change.
- **type:** A short identifier for the change (for example, `feat`, `fix`, etc.).
- **(scope):** An optional scope that indicates the area of the code affected.
- **Title:** A brief description of the change.
- **Description:** An optional, more detailed explanation of the change.

Below is a table that summarizes the available commit types with their corresponding emoji, type, and description. Each row also includes a mock commit command that you can use as a template when committing.

------

#### Commit Types

| Emoji             | Type             | Description              | Sample Commit Command                                        |
| ----------------- | ---------------- | ------------------------ | ------------------------------------------------------------ |
| :sparkles:        | feat             | Features                 | `git commit -m ":sparkles: feat(api): Add new endpoint\n\nFeatures"` |
| :bug:             | fix              | Bug Fixes                | `git commit -m ":bug: fix(parser): Correct error in parsing\n\nBug Fixes"` |
| :books:           | docs             | Documentation            | `git commit -m ":books: docs(readme): Update installation instructions\n\nDocumentation"` |
| :gem:             | style            | Styles                   | `git commit -m ":gem: style(ui): Improve button styles\n\nStyles"` |
| :package:         | refactor         | Code Refactoring         | `git commit -m ":package: refactor(auth): Simplify authentication logic\n\nCode Refactoring"` |
| :racehorse:       | perf             | Performance Improvements | `git commit -m ":racehorse: perf(db): Optimize query performance\n\nPerformance Improvements"` |
| :rotating_light:  | test             | Tests                    | `git commit -m ":rotating_light: test(api): Add tests for new endpoint\n\nTests"` |
| :wrench:          | build            | Builds                   | `git commit -m ":wrench: build(ci): Update build configuration\n\nBuilds"` |
| :gear:            | ci               | Continuous Integrations  | `git commit -m ":gear: ci(deploy): Fix deployment script\n\nContinuous Integrations"` |
| :recycle:         | chore            | Chores                   | `git commit -m ":recycle: chore(repo): Update project structure\n\nChores"` |
| :rewind:          | revert           | Reverts                  | `git commit -m ":rewind: revert(auth): Undo breaking change\n\nReverts"` |
| :arrow_double_up: | dependencies     | Dependencies             | `git commit -m ":arrow_double_up: dependencies(core): Upgrade library version\n\nDependencies"` |
| :arrow_double_up: | peerDependencies | Peer dependencies        | `git commit -m ":arrow_double_up: peerDependencies(ui): Update peer dependency versions\n\nPeer dependencies"` |
| :arrow_double_up: | devDependencies  | Dev dependencies         | `git commit -m ":arrow_double_up: devDependencies(test): Bump testing framework\n\nDev dependencies"` |
| :card_index:      | metadata         | Metadata                 | `git commit -m ":card_index: metadata(config): Add new metadata fields\n\nMetadata"` |
| :bookmark:        | version          | Version tag              | `git commit -m ":bookmark: version(release): Bump version to 2.0.0\n\nVersion tag"` |
| :lock:            | security         | Security                 | `git commit -m ":lock: security(api): Patch vulnerability in endpoint\n\nSecurity"` |
| :pencil:          | text             | Text                     | `git commit -m ":pencil: text(readme): Update project description\n\nText"` |
| :ambulance:       | critical         | Critical changes         | `git commit -m ":ambulance: critical(core): Urgent fix for production\n\nCritical changes"` |
| :ok_hand:         | review           | Code review              | `git commit -m ":ok_hand: review(utils): Adjust code per review comments\n\nCode review"` |
| :recycle:         | review           | Content review           | `git commit -m ":recycle: review(content): Revise documentation structure\n\nContent review"` |
| :bricks:          | other            | Other                    | `git commit -m ":bricks: other(misc): Miscellaneous updates\n\nOther"` |

------

#### How to Use

When making a commit, choose the commit type that best describes your change, and use the provided template. For example, if you're adding a new feature to an API component, you might use:

```bash
git commit -m ":sparkles: feat(api): Add new endpoint\n\nFeatures"
```

This standardization helps everyone on the team understand the nature of each change quickly and maintains a clean, consistent history for the project. Feel free to copy and modify any of the sample commands above to fit your needs.

### Pull Requests

In your PR's description you should follow the structure:

- **What**: what changes are in this PR;
- **Why**: why are these changes relevant;
- **How**: how have the changes been implemented;
- **Testing**: how has the changes been tested or how can the reviewer test the feature.

We highly encourage that you do a self-review prior to requesting a review. To do a self review click the review button in the top right corner, go through your code and annotate your changes. This makes it easier for the reviewer to process your PR.

## Branches workflow

This project has two key branches, they are:

- **main**: Untouchable branch. It contains a stable and production-ready code. It always reflects the latest production-ready release besides a tag version;
- **dev**: The integration branch where all feature branches are merged after review for the current major version. Serves as the central integration branch. All new features and fixes are merged into this branch via pull requests.

There also temporary branches:

- **feature/name**:
  - Branches for new features or improvements;
  - Must be created from the dev branch and always should be merged with the dev branch
  - Their names should be descriptive (e.g., `feature/add-user-auth`).
- **hotfix/semver**:
  - Branches for urgent fixes to the current stable version;
  - Must be created from the main branch and always should be merged with both main/dev branches;
  - Their names should use the current MAJOR/MINOR version from main and change PATCH (e.g., `hotfix/1.1.9`);
  - Must create a tag in main branch to the related version;
- **release/semver**:
  - Branches to launch a new release version (MAJOR/MINOR).
  - Must be created from the dev branch and always should be merged with both main/dev branches;
  - Their names should increase the MAJOR/MINOR version from main, PATCH will always be 0 (e.g., `release/1.2.0`);
  - Must create a tag in main branch to the related version.

### Versioning and branches

- `main`: always the last stable version (e.g., `1.2.3`);
  - `hotfix/<semver>`: always a PATCH version to current stable version.
- `dev`: always for current MAJOR version development (e.g., `1.x.x`);
  - `feature/<name>`: a bunch of features will produce, in future, a MINOR version.

#### (1) Creating a new feature for a MAJOR.MINOR version in development

> e.g.: you are in 1.1.x context.

1. On terminal, start the new feature branch:

   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/feature-name
   ```

2. Commit changes frequently:

   - Make small, focused commits with clear messages.

3. When you are ready, push your feature to remote repository and open a pull request:

   - Add a title and description following the rules;
   - The base branch must be `dev`.

4. After review and approval, your feature branch will be merged (merge commit, to keep granulation) into `dev`.

#### (2) Creating a hotfix for a STABLE version

> e.g.: you are moving from 1.1.2 to 1.1.3.

1. On terminal, start the new hotfix branch:

   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/<MAJOR>.<MINOR>.9
   ```

2. Commit changes frequently:

   - Make small, focused commits with clear messages.

3. When you are ready, push your feature to remote repository and open a pull request:

   - Add a title and description following the rules;
   - The base branch must be `main`.

4. After review and approval, your feature branch will be merged (squash) into `main`;

5. Then, reviewer must to propagate changes to dev:

   ```bash
   git checkout dev
   git pull origin dev
   git merge main
   git push origin dev
   ```

#### (3) Launching a new MINOR version

> e.g.: you are moving from 1.2.x to 1.3.0.

1. On terminal, start the new hotfix branch:

   ```bash
   it checkout dev
   git pull origin dev
   git checkout -b release/<MAJOR>.2.0
   ```

2. Commit changes frequently:

   - Make small, focused commits with clear messages.

3. When you are ready, push your feature to remote repository and open a pull request:

   - Add a title and description following the rules;
   - The base branch must be `main`.

4. After review and approval, your feature branch will be merged (squash) into `main`;

5. Then, the reviewer must to create a new tag on `main` branch to the release and propagate changes to dev;

   ```git
   git checkout main
   git pull origin main
   git tag -a vMAJOR.2.0 -m "Release version MAJOR.2.0"
   git push origin vMAJOR.2.0

   git checkout dev
   git pull origin dev
   git merge main
   git push origin dev
   ```

#### (4) Launching a new MAJOR version

> e.g.: you are moving from 1.x.x to 2.x.x.

1. Create a new branch from stable version (must be `MAJOR.x.x`) and push to remote repository:

   ```bash
   git checkout main
   git pull origin main
   git checkout -b v1.x.x
   git push -u origin v1.x.x
   ```

2. Now `v1.x.x` will be the development branch to version 1, and the `dev` branch will be related to version 2. When ready on `dev` branch a release will change the `main` to stable version as version 2, and so on.

## Code Review Guidelines

- Provide constructive, respectful feedback;
- Discuss improvements and suggest changes when necessary;
- Strive for clarity and maintain a collaborative atmosphere.

## Additional Information

- **Questions or Issues:** Open an issue if you have any questions or encounter problems;
- **Documentation:** Ensure any new feature or fix is accompanied by appropriate documentation and tests;
- **Thank You:** We appreciate every contribution, no matter the size.

------

By adhering to these guidelines, we ensure a consistent and efficient workflow that benefits all contributors. Thank you for helping us make this project even better!

**Happy coding 😆!**
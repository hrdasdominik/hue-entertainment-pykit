## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag `enhancement`. Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Switch to the dev branch 
```sh
git checkout dev
```
3. Create your Feature Branch
```sh
git checkout -b feature/AmazingFeature
```
4. Commit your Changes 
```sh
git commit -m 'Add some AmazingFeature'
```
5. Push to the Branch 
```sh
git push origin feature/AmazingFeature
```
6. Open a Pull Request to `dev` branch

Also, the `Discussions` section on GitHub is open for conversations, and the `Issues` section is available for reporting problems or discussing improvements.

## Publishing a release

Package versions are derived from Git tags using setuptools-scm. Do not add a fixed
version to `pyproject.toml`.

1. Merge the changes to `main` and wait for CI to pass.
2. Create a GitHub release from the intended commit on `main` with a new version
   tag, such as `v0.9.5b2` for a beta or `v0.9.5` for a stable release. Choose a
   version that has not already been published to PyPI.
3. Publish the release (including prereleases). The publishing workflow builds the
   package from that tag, checks that its version matches, and uploads it to PyPI.

The release title does not determine the package version; the Git tag does. Draft
releases do not publish packages. Builds between tags receive development versions.
For local builds, use a Git clone with its history and tags, or a generated source
distribution.

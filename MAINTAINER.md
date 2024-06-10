
### Releases

To make a release edit the `src/pytest_checklist.py/__about__.py` file
for the new version.

Test the build works:

```sh
hatch build
```

Then commit and tag. Then you can build and publish again.

```sh
hatch build
hatch publish
```

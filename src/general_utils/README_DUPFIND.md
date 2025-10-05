










# Duplicate finder - Notes

### Bash example

#### Strict checking (recursive)

```bash
find . -type f -print0 | xargs -0 sha256sum | sort | awk -F'  ' '
{
    hash = $1
    file = $2
    count[hash]++
    files[hash] = files[hash] "\n" file
}
END {
    for (hash in count)
        if (count[hash] > 1)
            print "Duplicate hash:", hash, "\nFiles:" files[hash] "\n"
}'
```

#### Strict checking (non-recursive)

```bash
find . -maxdepth 1 -type f -print0 | xargs -0 sha256sum | sort | awk -F'  ' '
{
    hash = $1
    file = $2
    count[hash]++
    files[hash] = files[hash] "\n" file
}
END {
    for (hash in count)
        if (count[hash] > 1)
            print "Duplicate hash:", hash, "\nFiles:" files[hash] "\n"
}'
```








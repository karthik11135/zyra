# 🌱 zyra 🌱

**Zyra** is a version control system built from scratch in Python.

Why the name **zyra**? it is a random gpt suggestion which looked snappy to me. 

---

## 🚀 Installation 🚀

If you are interested to see how this works, you can start by installing zyra using one of the following ways.

### 1. Using pip

[Link to the package](https://pypi.org/project/zyra-tool/)
```bash
pip install zyra-tool
```
After you are done using zyra, you can uninstall it using:

```bash
pip uninstall zyra-tool
```

So that your glorious storage is not eaten up. 

### 2. Using Docker

Make sure you have docker installed already.

```bash

# Clone the repo
git clone https://github.com/karthik11135/zyra.git

# Change your directory
cd zyra

# Build the dockerfile
docker build --no-cache -t zyra .

# Run interactively with volume mounted to your current path
docker run -it -v $(pwd):/app zyra
```

Or with Docker Compose:

```bash
git clone https://github.com/karthik11135/zyra.git
cd zyra
docker compose up run zyracli
```

### 3. Clone from github (RECOMMENDED)

If you don’t have Docker, you can create an executable directly:

```bash
git clone https://github.com/karthik11135/zyra.git
cd zyra
pip install -r requirements.txt
chmod +x zyra.py
alias zyra=./zyra.py
```

Here is the source code [zyratool](https://github.com/karthik11135/zyra/releases) in github.

Now you can use zyra like a command in your terminal

> ⚠️ Ensure you’re in the same directory to run commands.
> Usage: `zyra <subcommand>`

---

## 🚀 Quick start 🚀

Once you have installed and have an interactive shell, you can start running commands. The folders you create will be created in your current directory because of the volume mount (if you are using docker).

```bash
mkdir example
cd example
touch ex1.txt ex2.txt

zyra init
zyra add ex1.txt ex2.txt
zyra status
zyra commit -m "first commit"
```

Congratulations 🎉 You just created your first commit with my zyra.

---

## Complex example

```bash
mkdir example
cd example
touch ex1.txt ex2.txt
(add some txt)
zyra init
zyra add ex1.txt
zyra commit -m "master commit"
zyra all-commits
zyra create-branch dev
zyra switch dev
zyra add ex2.txt
zyra commit -m "dev commit"
zyra all-commits
zyra b-commits (branch specific commits)
(Change the text of ex2.txt)
zyra add ex2.txt
zyra commit -m "dev second commit"
zyra b-commits
zyra switch master
```

## Command Reference

(See `/cmds/commands.py` for implementation details)
While running these commands unhide your `.git` folder to see how files are changing inside. (if you are interested)

| Command           | Description                                                  | Example                            |
| ----------------- | ------------------------------------------------------------ | ---------------------------------- |
| **init**          | Initializes an empty repository and creates a master branch. | `zyra init`                        |
| **cat-file**      | Displays content of an object (blob, commit, tag, tree).     | `zyra cat-file <sha>`              |
| **hash-object**   | Computes the hash of a file and optionally writes it.        | `zyra hash-object -w <file>`       |
| **log**           | Displays commit history from a given commit.                 | `zyra log <commit_sha>`            |
| **checkout**      | Checks out a commit/tree into a directory.                   | `zyra checkout <commit_sha> <dir>` |
| **show-ref**      | Lists references (branches, tags, etc.).                     | `zyra show-ref`                    |
| **tag**           | Creates a tag or lists existing tags.                        | `zyra tag -a <tag_name> <sha>`     |
| **rev-parse**     | Resolves a reference or object to its SHA.                   | `zyra rev-parse <ref>`             |
| **status**        | Shows current repo status (branch, staged changes, etc.).    | `zyra status`                      |
| **rm**            | Removes files from staging/working directory.                | `zyra rm <file>`                   |
| **add**           | Adds files to staging.                                       | `zyra add <file>`                  |
| **commit**        | Creates a commit with staged changes.                        | `zyra commit -m "msg"`             |
| **all-commits**   | Lists all commit objects in the repo.                        | `zyra all-commits`                 |
| **branch**        | Shows all branches and highlights the current one.           | `zyra branch`                      |
| **switch**        | Switches to another branch.                                  | `zyra switch <branch>`             |
| **create-branch** | Creates a branch and updates HEAD.                           | `zyra create-branch <branch>`      |
| **b-commits**     | Displays all commits in the current branch.                  | `zyra b-commits`                   |

--- 

## 

Just like git, zyra also stores data by compressing and hashing objects. There are four objects mainly - blob, tree, commit and tag. 

Example: Let's see how a file `one.txt` with contents `"Hi there"` is stored:


At a high level, zyra compresses file contents and stores them as objects inside a folder in the repo (named as `.git`, though any name could be used). The `.git` name is a convention many editors and tools recognize, which is why zyra uses it. 

`one.txt` with contents `Hi there`

1. Zyra computes the content's size: `len("Hi there") = 8`.
2. Converts the contents into a binary string
3. Format: b'{object_type}{size}\x00{content}'. The object type is blob in this case because we are trying to store contents of a file
4. Compresses with **zlib**.

Example: b'blob8 Hi there'

5. Also, computes the **SHA1 hash** of b'{object_type}{size}\x00{content}'.
6. Store the zlib compressed binary file in:

   ```
   .git/objects/<sha[0:2]>/<sha[2:]>
   ```

More details: `common/objects.py`

Very similarly tree, commit and tag objects are also stored. 

A brief gpt explanation on what's the difference between these objects: 

- Blob — stores raw file contents (data), addressed by its SHA.
- Tree — records directory entries (names, modes) and points to blobs/subtrees.
- Commit — snapshot pointing to a tree with metadata (parent(s), author, message).
- Tag — named reference (lightweight or annotated) pointing to another object with optional message/metadata.


---

## Relationships between objects

### Files → Blobs → Tree

```
   file1.txt  file2.txt
       │          │
       ▼          ▼
     (blob)    (blob)
        \        /
         ▼      ▼
         ┌───────────┐
         │   Tree    │ 
         └───────────┘
```

### Commit Structure

```
 ┌───────────┐
 │  Commit   │───► This object is stored in the path of its own sha
 │-----------│
 │ tree: sha │───► (Tree)
 │ parent:   │───► (Prev Commit)
 │ message   │
 └───────────┘
```

### Tag Reference

```
   (Tag) ───► (Blob)
     │
     ▼
   (Commit)
```

**Overall Flow:**

```
 File → Blob → Tree → Commit
```

### Issues Reporting and Contributions

While playing around with zyra you **might** be bombarded with errors if you run commands with unexpected arguments etc. While I've tried my best to cover edge cases and provide error messages, if there are any cases where I've missed, kindly open an issue on github. 

---

##### <span style="color: blue; background-color: yellow;">Thank you for reading</span> 

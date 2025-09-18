# 🌱 zyra 🌱

**Zyra** is a version control system built from scratch in Python.

Why the name **zyra**? The name zyra is snappy and inspired by plants. In _League of Legends_, Zyra is a plant-themed champion. Since Git also uses tree structures (objects, roots, branches), this felt like an acceptable analogy for me.

---

### Table of Contents

  - [⚙️ High level basics of how a version control system like git operates its storage using objects](#️-high-level-basics-of-how-a-version-control-system-like-git-operates-its-storage-using-objects)
  - [Where are the files stored?](#where-are-the-files-stored)
  - [Object Relationships](#object-relationships)
    - [Files → Blobs → Tree](#files--blobs--tree)
    - [Commit Structure](#commit-structure)
    - [Tag Reference](#tag-reference)
  - [🚀 Installation 🚀](#-installation-)
    - [Using Docker](#using-docker)
    - [Manual way](#manual-way)
  - [🚀 Quick start 🚀](#-quick-start-)
  - [⚡ Complex example](#-complex-example)
  - [🛠️ Command Reference](#️-command-reference)
  - [Challenges Faced](#challenges-faced)
  - [Why Git?](#why-git)

---

## High level basics of how a version control system like git operates its storage using objects

At its core, Zyra follows the same architecture as Git.

1. Everything is stored in **objects**.
2. There are **four types of objects**:
   - **Blob** → Stores file contents.
   - **Tree** → Represents the entire working directory (contains items - leaves (blob or tree)).
     - Reference: `common/tree/tree_obj.py`
   - **Commit** → Represents a snapshot (tree's sha, parent’s sha, commit message, etc.).
   - **Tag** → Human-readable tags for objects. These are basically other names given to commits so that its easier to reference. 
3. An **index file** is used for staging. The entire metadata is stored in this binary file
   - Reference: `/stage`

---

## Where are the files stored?

Zyra stores data by compressing and hashing objects like git.

Example: Let's see how a file `one.txt` with contents `"Hi there"` is stored:

1. Zyra computes its size: `len("Hi there") = 8`.
2. Converts the contents into a binary string
3. Format: b'{object_type}{size}\x00{content}'. The object type is blob in this case
4. Compresses with **zlib**.

Example: b'blob8 Hi there'

5. Also, compute the **SHA1 hash** of b'{object_type}{size}\x00{content}'.
6. Store the zlib compressed binary file in:

   ```
   .git/objects/<sha[0:2]>/<sha[2:]>
   ```

More details: `common/objects.py`

Very similarly tree, commit and tag objects are also stored. 

---

## Object Relationships

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

---

## 🚀 Installation 🚀

If you are interested to see how this works, you need to install zyra using one of the following approaches

### Using Docker

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

### Manual way

If you don’t have Docker, you can create an executable directly:

```bash
git clone https://github.com/karthik11135/zyra.git
cd zyra
pip install -r requirements.txt
chmod +x zyra.py
alias zyra=./zyra.py
```

Now you can use zyra like a command

> ⚠️ Ensure you’re in the same directory to run commands.
> Usage: `zyra <subcommand>`

---

## 🚀 Quick start 🚀

Once you have installed and have an interactive shell, you can test it out. The folders you create will be created in your current directory because of the volume mount (if you are using docker).

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

## ⚡ Complex example

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

## 🛠️ Command Reference

(See `/cmds/commands.py` for implementation details)
While running these commands unhide your `.git` folder to see how things are changing inside it.

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

## Challenges Faced

1. Writing the **staging area** logic.
2. Understanding Git’s branching model (solved by using `.git/branches` alongside `/refs/heads`).
3. Managing **file metadata**, which is verbose (much of it unused).
4. Converting the **index file → tree SHA** was tricky.

---

## Why Git?

Git was referenced often because Zyra follows the same architecture, so understanding Git internals was crucial to implementing Zyra.

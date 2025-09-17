# 🌱 Zyra

**Zyra** is a version control system built from scratch in Python.  
The name *Zyra* is short, snappy, and inspired by plants. In *League of Legends*, Zyra is a plant-themed champion. Since Git also uses tree structures (objects, roots, branches), this felt like an acceptable analogy for me.

---

## ⚙️ How Zyra Works

At its core, Zyra follows the same architecture as Git.

1. Everything is stored in **objects**.
2. There are **four types of objects**:
   - **Blob** → Stores file contents.  
   - **Tree** → Represents the entire working directory (contains items - leaves).  
     - Reference: `common/tree/tree_obj.py`  
   - **Commit** → Represents a snapshot (tree's sha, parent’s sha, commit message, etc.).  
   - **Tag** → Human-readable tags for objects.  
3. An **index file** is used for staging.  
   - Reference: `/stage`

---

## 📦 Storage Model

Zyra (like Git) stores data by compressing and hashing objects.

Example: storing a file `one.txt` with contents `"Hi there"`:

1. Compute size: `len("Hi there") = 8`.
2. Wrap in a **blob object**.
3. Compress with **zlib**.
4. Format:  b'{object_type}{size}\x00{content}'

Example: b'blob8 Hi there'

5. Compute the **SHA hash** of contents.
6. Store in:

   ```
   .git/objects/<sha[0:2]>/<sha[2:]>
   ```

👉 More details: `common/objects.py`

---

## 🖼️ Object Relationships

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
         │ (directory│
         │ snapshot) │
         └───────────┘
```

### Commit Structure

```
 ┌───────────┐
 │  Commit   │
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

## 🚀 Installation

### Using Docker

If you’ve cloned the repo and have Docker:

```bash
# Build the dockerfile
docker build --no-cache -t zyra .

# Run interactively with volume mounted to your current path
docker run -it -v $(pwd):/app zyra
```

Or with Docker Compose:

```bash
docker compose up run zyracli
```

### Without Docker

If you don’t have Docker, you can create an executable directly:

```bash
pip install -r requirements.txt
chmod +x zyra.py
alias zyra=./zyra.py
```

> ⚠️ Ensure you’re in the same directory to run commands.
> Usage: `zyra <subcommand>`

---

## ⚡ Quick Start

```bash
mkdir example
cd example
touch ex1.txt ex2.txt

zyra init
zyra add ex1.txt ex2.txt
zyra status
zyra commit -m "first commit"
```

🎉 Congratulations! You just created your first commit with Zyra.

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
17 commands have been implemented

| Command           | Description                                                  | Example                                 |
| ----------------- | ------------------------------------------------------------ | --------------------------------------- |
| **init**          | Initializes an empty repository and creates a master branch. | `zyra init`                             |
| **cat-file**      | Displays content of an object (blob, commit, tag, tree).     | `zyra cat-file <sha>` |
| **hash-object**   | Computes the hash of a file and optionally writes it.        | `zyra hash-object -w <file>`            |
| **log**           | Displays commit history from a given commit.                 | `zyra log <commit_sha>`                 |
| **checkout**      | Checks out a commit/tree into a directory.                   | `zyra checkout <commit_sha> <dir>`      |
| **show-ref**      | Lists references (branches, tags, etc.).                     | `zyra show-ref`                         |
| **tag**           | Creates a tag or lists existing tags.                        | `zyra tag -a <tag_name> <sha>`          |
| **rev-parse**     | Resolves a reference or object to its SHA.                   | `zyra rev-parse <ref>`                  |
| **status**        | Shows current repo status (branch, staged changes, etc.).    | `zyra status`                           |
| **rm**            | Removes files from staging/working directory.                | `zyra rm <file>`                        |
| **add**           | Adds files to staging.                                       | `zyra add <file>`                       |
| **commit**        | Creates a commit with staged changes.                        | `zyra commit -m "msg"`                  |
| **all-commits**   | Lists all commit objects in the repo.                        | `zyra all-commits`                      |
| **branch**        | Shows all branches and highlights the current one.           | `zyra branch`                           |
| **switch**        | Switches to another branch.                                  | `zyra switch <branch>`                  |
| **create-branch** | Creates a branch and updates HEAD.                           | `zyra create-branch <branch>`           |
| **b-commits**     | Displays all commits in the current branch.                  | `zyra b-commits`                        |

---

## ⚡ Challenges Faced

1. Writing the **staging area** logic.
2. Understanding Git’s branching model (solved by using `.git/branches` alongside `/refs/heads`).
3. Managing **file metadata**, which is verbose (much of it unused).
4. Converting the **index file → tree SHA** was tricky.

---

## 🌳 Why Git?

Git was referenced often because Zyra follows the same architecture, so understanding Git internals was crucial to implementing Zyra.


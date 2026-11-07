# AWS EKS — Storage — Guide

Total length: **12:28**

**Video:** [`EKS-Storage.mp4`](EKS-Storage.mp4), 1920×1080, 30 fps, with chapter markers. In VLC use *Playback → Chapter*.
**Editable drawings:** [`EKS-Storage.excalidraw`](EKS-Storage.excalidraw). Open it at excalidraw.com with *Menu → Open*; each scene is a named frame.
**Source:** `EKS/AWS_EKS_fundamentals/`. Chapters follow the numbered files in `concepts/storage/` (00 basics, 01-ebs … 07-fsx-ontap, 08 cleanup, 09 diagrams) and `labs/02–08`, in order.

**Execution status:** **All 7 storage labs were executed live** (EBS, EFS, Mountpoint S3, S3 Files, FSx for OpenZFS / Lustre / NetApp ONTAP), plus cleanup. Timings are measured.

### How to use this guide
- Each **[mm:ss]** line is the on-screen caption, with its exact time in this video.
- *On screen* describes the animation; the paragraph under it explains the idea and the kubectl/YAML/AWS pieces involved.
- Tags follow the source notes: **[LIVE]** = measured on a real EKS cluster, **[W]** = stated by the EKS Workshop, **[BG]** = background knowledge (verify before relying on it). Account IDs and IPs are never shown.

## Chapters

| Starts | Chapter | Length | Source video |
|---|---|---|---|
| 00:00 | [Introduction](#introduction) | 00:12 | `00-intro` |
| 00:12 | [Chapter 1 — Kubernetes storage & CSI](#chapter-1--kubernetes-storage--csi) | 01:33 | `S01-k8s-storage-basics-csi` |
| 01:46 | [Chapter 2 — Amazon EBS & StatefulSets](#chapter-2--amazon-ebs--statefulsets) | 01:34 | `S02-ebs` |
| 03:20 | [Chapter 3 — Amazon EFS: shared storage](#chapter-3--amazon-efs-shared-storage) | 01:25 | `S03-efs` |
| 04:46 | [Chapter 4 — Mountpoint for Amazon S3](#chapter-4--mountpoint-for-amazon-s3) | 01:31 | `S04-mountpoint-s3` |
| 06:18 | [Chapter 5 — Amazon S3 Files](#chapter-5--amazon-s3-files) | 01:12 | `S05-s3-files` |
| 07:31 | [Chapter 6 — Amazon FSx for OpenZFS](#chapter-6--amazon-fsx-for-openzfs) | 01:14 | `S06-fsx-openzfs` |
| 08:45 | [Chapter 7 — Amazon FSx for Lustre](#chapter-7--amazon-fsx-for-lustre) | 01:13 | `S07-fsx-lustre` |
| 09:59 | [Chapter 8 — FSx for NetApp ONTAP](#chapter-8--fsx-for-netapp-ontap) | 01:17 | `S08-fsx-ontap` |
| 11:17 | [Chapter 9 — Cleanup & Choosing Storage](#chapter-9--cleanup--choosing-storage) | 01:10 | `S09-cleanup-and-choosing` |

---

## Introduction

**Starts at 00:00** · length 00:12 · source `00-intro` · hook: *"Seven AWS storage services, one Kubernetes pattern: CSI"*

**What you'll learn.** This opening card lists the nine storage chapters, in the same order as the numbered folders in `concepts/storage/` (00-basics, 01-ebs … 07-fsx-ontap, 08-cleanup). Per `EXECUTION_SUMMARY.md`, all seven storage labs were run [LIVE] on the `eks-workshop` cluster (K8s 1.33, 3 × m5.large), so the timings in the video are measurements. Start with Chapter 1: every later chapter reuses its PVC → StorageClass → CSI picture.

### What this video covers

**[00:07]** Every lab here was executed live; timings are measured.

> *On screen:* The nine chapter titles type in down two columns, then the caption confirms every storage lab was run live.

Storage is the largest topic in this study log: seven AWS options, each with its own CSI driver, plus a cleanup chapter. The order matters. Block storage (EBS) comes first, then shared file systems (EFS), then S3-based options (Mountpoint, S3 Files), then the three FSx file systems. Each chapter reuses the same Kubernetes objects, so most of the learning happens in Chapter 1.


---

## Chapter 1 — Kubernetes storage & CSI

**Starts at 00:12** · length 01:33 · source `S01-k8s-storage-basics-csi` · hook: *"Where do you keep data that must outlive the pod?"*

**What you'll learn.** This chapter follows `concepts/storage/00-kubernetes-storage-basics.md` and `animations/00-csi-and-provisioning.html`, with live evidence from the EBS lab (`01-ebs/01-statefulsets.md`, `02-ebs-csi-driver.md`). It teaches the storage vocabulary (Volume, PV, PVC, StorageClass, CSI driver), the two phases of a volume's life, dynamic vs static provisioning, and access modes. Nothing here needs prior storage knowledge, but the controller idea from *Exposing Applications* helps: every arrow is a controller reacting to an object.

### A container's disk is a whiteboard

**[00:19]** Before the lab, MySQL kept its data in an emptyDir volume.

> *On screen:* A pod box for `catalog-mysql-0` appears with a dashed `emptyDir /var/lib/mysql` volume inside it.

Before the lab, the catalog MySQL StatefulSet stored its database in an `emptyDir` volume. An `emptyDir` is created when the pod lands on a node and deleted when the pod leaves, for any reason. It solves "lost on container restart" but not "lost on pod replacement". `kubectl describe statefulset -n catalog catalog-mysql` shows `Type: EmptyDir` and `Volume Claims: <none>`.

**[00:21]** kubectl delete pod: the StatefulSet recreates a pod with the SAME name...

> *On screen:* A yellow `test.txt = 123` card points into the volume, then the pod fades out and back in as it is deleted and recreated.

The live test wrote `echo 123 > /var/lib/mysql/test.txt`, then ran `kubectl delete pod catalog-mysql-0`. The StatefulSet immediately created a replacement with the same name, `catalog-mysql-0`, but a new uid and a new IP (10.0.3.202 → 10.0.4.78). This was run on the `primary` cluster with the same manifest [LIVE].

**[00:24]** ...but the file is gone [LIVE]. Name survived, data did not.

> *On screen:* The file card disappears and a red `No such file or directory` box appears beside the pod.

`cat /var/lib/mysql/test.txt` failed after the replacement. That one test teaches two separate lessons: a StatefulSet keeps the pod's identity (name, ordinal, DNS name), but it does not keep data unless the volume is persistent. Fixing that, with a PVC backed by real storage, is what the EBS lab does.

### Three questions, three objects

**[00:30]** PVC = request, PV = real storage, StorageClass = how to make more (via a CSI driver).

> *On screen:* Three boxes, PVC, PV and StorageClass, pop in with their question and a one-line description, then the live EBS-lab example types in below.

Kubernetes splits storage into three questions. **What do I need?** is the PVC, a request by size and access mode. **What exists?** is the PV, a piece of real storage registered in the cluster. **How do I get more?** is the StorageClass, which names a CSI driver and its settings. In the live EBS lab the claim was `data-catalog-mysql-ebs-0`, the PV was a 30 GiB volume `pvc-6d370afd-…`, and the class was `ebs-csi-default-sc`.

### The life of a volume (dynamic provisioning)

**[00:38]** You create a PVC that names a StorageClass.

> *On screen:* The first box, `PVC (your request)`, appears with a red token above it, then a `StorageClass` box draws in beside it with an arrow.

The life of a dynamically provisioned volume starts with you writing a PVC, usually through a StatefulSet's `volumeClaimTemplates`. The claim names a StorageClass, or uses the default class when `storageClassName` is omitted. The StorageClass's `provisioner` field, here `ebs.csi.aws.com`, tells Kubernetes which driver should act on the claim.

**[00:40]** The CSI controller's provisioner sees a claim for its driver.

> *On screen:* The token moves on to a violet `CSI controller (provisioner)` box.

The CSI controller runs a generic sidecar called `csi-provisioner`. It watches PVCs and picks up the ones whose StorageClass names its driver. It is a controller in exactly the same sense as the AWS Load Balancer Controller: the PVC spec is the desired state, and the controller works until reality matches it.

**[00:43]** It calls the AWS API with its IAM role and creates the real volume.

> *On screen:* An `AWS API CreateVolume` box appears and the token travels to it.

The provisioner asks the AWS-specific plugin (`ebs-plugin`) to call the EC2 API (`CreateVolume`). It is allowed to because the controller's ServiceAccount is bound to an IAM role through IRSA, so no access keys live in the cluster. Without that role the driver falls back to the node's IAM role, which normally lacks EBS permissions; the symptom is a PVC stuck `Pending` with `AccessDenied` in the controller logs [BG].

**[00:45]** It writes a PV object pointing at the volume; the claim binds.

> *On screen:* A green `PV object volumeHandle` box appears below the AWS box and the token drops onto it.

Once the real volume exists, the provisioner writes a PV whose `csi.volumeHandle` is the AWS volume ID (`vol-…` for EBS). The PVC then binds to that PV. Binding is one-to-one: one claim, one PV, one piece of storage.

**[00:47]** Phase 2 starts when a pod needs the claim.

> *On screen:* A dashed green arrow curves back from the PV to a new `Pod uses the PVC` box on the second row.

Phase 1 (create the storage) is finished. Phase 2 (make it usable inside a container) only starts when a pod references the claim in its `volumes:` list. Until then the storage exists but is not attached or mounted anywhere.

**[00:49]** A pod uses the claim; the scheduler picks a node.

> *On screen:* A `Scheduler picks a node` box draws in next to the pod box and the token moves to it.

The scheduler places the pod on a node. For EBS this choice also decides where the disk can live, which is why the EBS StorageClass uses `WaitForFirstConsumer` (Chapter 2): the disk is created only after the node, and therefore its Availability Zone, is known.

**[00:52]** Block storage (EBS) is first attached to that node.

> *On screen:* A violet `csi-attacher attach disk` box appears and the token moves on.

Block storage must be attached to the instance before it can be used. The `csi-attacher` sidecar watches `VolumeAttachment` objects and asks the plugin to call `AttachVolume`. Network file systems such as EFS or FSx skip this step entirely; their CSIDriver objects say `attachRequired: false`.

**[00:54]** The node plugin formats and mounts it; the container sees a directory.

> *On screen:* The last box, `node plugin format + mount`, appears and the token arrives there.

On the node, the CSI node plugin (a DaemonSet pod) formats the device the first time (ext4 by default for EBS) and mounts it where kubelet asks. The container just sees a directory, such as `/var/lib/mysql`, and has no idea a cloud disk is behind it.

**[00:57]** Every storage lab is a variation of this picture.

> *On screen:* A grey note types in under the diagram: block disks attach, network file systems just mount, S3-based ones translate or sync.

Every later chapter is a variation of these nine boxes. EBS uses all of them. EFS and FSx drop the attach step, because a network file system only needs a mount. Mountpoint for S3 and S3 Files put a translation or synchronisation layer between file calls and S3 objects.

### Two halves of every CSI driver

**[01:01]** The controller talks to AWS; the node plugin does the work on each node.

> *On screen:* Two large panels appear: `Controller (a Deployment)` on the left and `Node plugin (a DaemonSet)` on the right, each listing its jobs.

Every CSI driver has two halves. The **controller** (a Deployment) creates, deletes, attaches and expands the cloud resource by calling the provider's API; for EBS its sidecars are csi-provisioner, csi-attacher, csi-resizer and csi-snapshotter. The **node plugin** (a DaemonSet, one pod per node) registers the driver with kubelet and does the format-and-mount work locally.

**[01:06]** Live: the EBS add-on went CREATING -> ACTIVE in 44 s, with 2 controller pods + 3 node pods.

> *On screen:* A yellow IRSA banner draws in under both panels, then the live add-on result appears in the caption.

The driver was installed as an EKS add-on: `aws eks create-addon --addon-name aws-ebs-csi-driver --service-account-role-arn <role>`. It went `CREATING` → `ACTIVE` in 44 s (version v1.67.1-eksbuild.1). It created `ebs-csi-controller` with 2/2 replicas on different nodes and the `ebs-csi-node` DaemonSet with 3 pods, one per node [LIVE]. Only the controller needs AWS permissions; the role's trust policy trusts just its ServiceAccount.

### Dynamic vs static provisioning

**[01:14]** Dynamic: the claim triggers creation. Static: you describe storage that already exists.

> *On screen:* Two panels compare provisioning modes: green DYNAMIC (driver creates storage) and yellow STATIC (storage exists, admin writes a PV).

With **dynamic** provisioning the claim triggers creation: an EBS volume, an EFS access point, an FSx OpenZFS volume or an ONTAP volume. With **static** provisioning the storage already exists (a bucket, a Lustre or S3 Files file system), so you write the PV yourself and the PVC binds to it by name. The live labs used static provisioning for Mountpoint S3, S3 Files and FSx for Lustre.

**[01:18]** So pre-built file systems and buckets survive; only driver-made pieces go.

> *On screen:* A wide box types in under both panels explaining what `reclaimPolicy: Delete` and `Retain` do when a PVC is deleted.

`reclaimPolicy` decides what happens when the claim is deleted. With `Delete`, the driver removes what *it* created: the EBS volume, or the EFS access point but not the file system. With `Retain`, the PV becomes `Released` and you clean up by hand. So pre-built file systems and buckets survive teardown, and only driver-made pieces disappear.

### Access modes, and seven AWS options

**[01:23]** EBS is ReadWriteOnce; shared file systems like EFS are ReadWriteMany.

> *On screen:* Four access-mode tiles pop in (RWO, ROX, RWX, RWOP), each with its full name and which AWS storage uses it.

Access modes describe how many nodes may mount a volume. `ReadWriteOnce` means one node read-write (EBS). `ReadOnlyMany` is many nodes read-only. `ReadWriteMany` is many nodes read-write: EFS, the FSx file systems and the S3-based options. `ReadWriteOncePod` restricts a volume to a single pod [BG]. Asking for RWX on an EBS-backed class does not work, because EBS is a block disk attached to one instance.

**[01:25]** The next chapters run each of these on a real EKS cluster.

> *On screen:* A row of seven orange tiles appears along the bottom, one per AWS storage option covered next.

The workshop lists seven options: EBS (block, one AZ, EC2 only), EFS (shared NFS, multi-AZ, Fargate and EC2), FSx for NetApp ONTAP, S3 Files, Mountpoint for S3, FSx for Lustre (parallel HPC/ML) and FSx for OpenZFS [W]. The following chapters take them one at a time in that folder order. Chapter 9 compares them side by side.

### Key takeaways  `[01:31]`

- emptyDir dies with the pod; persistent data needs a PV
- PVC = request, PV = storage, StorageClass = how to make it
- CSI: controller calls AWS, node plugin mounts on each node
- Dynamic creates storage; static binds to what exists

---

## Chapter 2 — Amazon EBS & StatefulSets

**Starts at 01:46** · length 01:34 · source `S02-ebs` · hook: *"How does a database keep its disk when its pod is replaced?"*

**What you'll learn.** This chapter follows `concepts/storage/01-ebs/` in file order: `01-statefulsets.md`, `02-ebs-csi-driver.md`, `03-statefulset-with-ebs-volume.md`, plus `labs/02-storage-ebs.md`. Everything shown was run [LIVE]: the add-on install (44 s), the 26-second provisioning timeline, the persistence test, the AZ lock, online expansion to 32Gi and deletion. It builds directly on Chapter 1's dynamic-provisioning picture; EBS is the case where the *attach* step really happens.

### StatefulSets: named pods, each with its own locker

**[01:52]** Ordered start: web-1 is not even created until web-0 is Ready.

> *On screen:* Three pod boxes `web-0`, `web-1`, `web-2` appear left to right with their start times, joined by arrows.

A StatefulSet is a team of named individuals, each with its own locker. With the default `podManagementPolicy: OrderedReady`, the live demo showed web-0 Pending at 09:05:11 and Ready at 09:05:14, web-1 created only then and Ready at 09:05:17, then web-2 [LIVE]. This ordering matters for clustered databases, where the primary should start before its replicas.

**[01:56]** Stable identity: a replaced pod keeps its name and its own claim.

> *On screen:* A line of text explains that deleting web-1 produces a new pod named web-1 again, with a new uid and IP but the same DNS name.

Deleting `web-1` produced a replacement with the same name (uid `59af0981` → `d752445e`). With a headless Service (`clusterIP: None`), each pod gets its own DNS name `web-N.web.<ns>.svc.cluster.local`, and that name followed the pod to its new IP [LIVE]. With `volumeClaimTemplates`, each ordinal also gets its own PVC, so `web-1` always comes back to `web-1`'s storage.

**[02:00]** Stopping and updates go in reverse, so ordinal 0 changes last.

> *On screen:* A second line appears: scale down and rollouts go highest ordinal first, web-2 → web-1 → web-0.

Scaling 3 → 1 terminated web-2 at 09:06:10 and web-1 at 09:06:11, keeping web-0. A rolling update restarted web-2, then web-1, then web-0 [LIVE]. Ordinal 0 is typically the primary, so it changes last. The workshop also notes that `volumeClaimTemplates` is immutable, which is why the lab creates a new StatefulSet `catalog-mysql-ebs` instead of editing the old one [W].

### Installing the EBS CSI driver add-on

**[02:05]** The add-on gets AWS permissions via IRSA: a role trusted only by ebs-csi-controller-sa.

> *On screen:* An install box `aws eks create-addon aws-ebs-csi-driver` leads to `ACTIVE in 44 s`, beside boxes for the controller (2/2) and the node DaemonSet (3).

The add-on needs an IAM role first: one with the AWS-managed `AmazonEBSCSIDriverPolicy`, whose trust policy allows only `system:serviceaccount:kube-system:ebs-csi-controller-sa` through the cluster's OIDC provider. EKS injects web-identity credentials into the controller pods, so the SDK can call STS without stored keys. The node plugin does not call the EC2 API, so it does not need this role.

**[02:08]** WaitForFirstConsumer: create the disk only after the pod's node (and AZ) is known.

> *On screen:* A wide StorageClass box lists `ebs-csi-default-sc`: gp3, ext4, WaitForFirstConsumer, reclaimPolicy Delete, allowVolumeExpansion true.

Enabling `defaultStorageClass` in the add-on configuration created `ebs-csi-default-sc` with no parameters, so the driver's defaults applied: gp3 and ext4 [LIVE]. `WaitForFirstConsumer` delays disk creation until a pod is scheduled, so the disk lands in that pod's AZ. With `Immediate` binding the disk could be created in a random AZ first and leave the pod unschedulable. The old in-tree `gp2` class (`kubernetes.io/aws-ebs`) still shows up in `kubectl get sc`, but the CSI class is the one to use.

### 26 seconds from apply to a running database

**[02:15]** 09:20:07 the StatefulSet creates the PVC: Pending, waiting for a consumer.

> *On screen:* A timeline axis from 0 to 26 s draws in; event box 1, `PVC Pending, no disk yet`, appears with its dot at 0 s.

At 09:20:07 the StatefulSet created PVC `data-catalog-mysql-ebs-0` and pod `catalog-mysql-ebs-0` together. The PVC event read `WaitForFirstConsumer: waiting for first consumer to be created before binding`, with no disk yet. That `Pending` state is normal, not an error.

**[02:17]** 09:20:10 the scheduler picks a node in us-west-2a first...

> *On screen:* Event box 2, `Pod scheduled, node in us-west-2a`, appears with its dot at 3 s.

At 09:20:10 the scheduler placed the pod on node `ip-10-42-112-69` in us-west-2a. The PVC picks up the annotation `volume.kubernetes.io/selected-node`, which tells the provisioner where the consumer will run. Order matters here: node first, disk second.

**[02:20]** ...then the provisioner creates the 30 GiB gp3 disk in that same AZ.

> *On screen:* Event box 3, `disk created in THAT node's AZ`, appears at the same 3 s mark.

In the same second, `ProvisioningSucceeded` reported `pvc-6d370afd-…`: a 30 GiB gp3 volume (3000 IOPS, 125 MB/s baseline) in us-west-2a [LIVE]. The volume's tags include `ebs.csi.aws.com/cluster=true` and `kubernetes.io/created-for/pvc/name=data-catalog-mysql-ebs-0`. The driver's IAM policy uses that first tag to limit which volumes it may delete.

**[02:22]** 09:20:13 csi-attacher attaches the disk to the EC2 instance.

> *On screen:* Event box 4, `AttachVolume succeeded`, appears with its dot at 6 s.

At 09:20:13 the pod event `SuccessfulAttachVolume` confirmed the attach. A cluster-scoped `VolumeAttachment` object now records driver, node and PV with `attached: true`. AWS lists the device as `/dev/xvdaa`, while Linux inside the pod sees `/dev/nvme1n1`, because Nitro instances expose EBS as NVMe devices [BG].

**[02:25]** Image pull (11 s), then the container starts...

> *On screen:* Event box 5, `container started`, appears at 24 s.

Most of the 26 seconds was not storage at all: pulling `mysql:8.0` took 11 s (09:20:19 → 09:20:30), and the container started at 09:20:31. Storage provisioning and attach together took about 6 s. When startup is slow, check the image pull before blaming the volume.

**[02:27]** 09:20:33 Running: 26 s total, on its own EBS disk.

> *On screen:* The last event box, `Pod Running`, appears with its green dot at 26 s.

At 09:20:33 the pod was Running: 26 s from `kubectl apply` to a database on its own disk [LIVE]. Inside the pod, `df -h /var/lib/mysql` showed `/dev/nvme1n1 30G 201M used`. The catalog ConfigMap was patched to `catalog-mysql-ebs:3306`, so the API used the new database.

### Delete the pod: the same disk comes back

**[02:32]** Write test.txt, then kubectl delete pod catalog-mysql-ebs-0.

> *On screen:* A node box shows pod `catalog-mysql-ebs-0` attached to an orange EBS volume, with `test.txt = 123` written under the pod.

The persistence test repeats Chapter 1's failed experiment, now on EBS: write `echo 123 > /var/lib/mysql/test.txt`, then `kubectl delete pod catalog-mysql-ebs-0` (09:21:46). The StatefulSet recreates the pod under the same name, and the same PVC still refers to the same PV and EBS volume.

**[02:35]** Same name, same claim, same disk: the data survived.

> *On screen:* The pod fades and returns, then a green result box shows `Ready again in 4 s`, `cat test.txt -> 123` and `12 products in DB`.

The replacement was Ready at 09:21:50, only 4 s later, because it landed on the same node where the volume was still attached [LIVE]. `cat test.txt` returned 123, `GET /catalog/products` returned HTTP 200, and `select count(*) from products` returned 12. If the replacement had landed on another node, the disk would first have been detached and re-attached, which takes longer [BG].

### The AZ lock: EBS lives in one Availability Zone

**[02:40]** The PV carries nodeAffinity: zone In [us-west-2a].

> *On screen:* Three AZ columns appear, each with a node; the EBS volume and the mysql pod sit in the first one.

The PV is pinned with `nodeAffinity: topology.kubernetes.io/zone In [us-west-2a]`. An EBS volume can only be attached to an instance in its own AZ, so Kubernetes may only run the pod there. You can see it with `kubectl get pv <pv> -o jsonpath='{.spec.nodeAffinity}'`.

**[02:44]** Cordon the only node in 2a and the pod cannot run anywhere else.

> *On screen:* The node in 2a is labelled `cordoned`, an arrow toward the other AZs is blocked, and a red `Pending` message types in.

The live test cordoned the only node in us-west-2a and deleted the pod. It stayed `Pending` with `0/3 nodes are available: 1 node(s) were unschedulable, 2 node(s) didn't match PersistentVolume's node affinity` [LIVE]. The other two healthy nodes cannot help, because the data is physically in 2a.

**[02:48]** Uncordon: Running 9 s later, data intact. Keep nodes in every AZ you use.

> *On screen:* The 2a node returns to normal and the pod runs again, with the lesson typed underneath.

After uncordoning, the pod was Running 9 s later with its data intact [LIVE]. The lesson: an EBS-backed pod can only run in its volume's AZ. Keep schedulable nodes in every AZ you use, and treat an AZ outage as "this database is down until the AZ returns or you restore from a snapshot" [BG]. For data that must be reachable from several AZs, use EFS or FSx.

### Grow it online, and know who deletes the disk

**[02:54]** kubectl patch pvc ... storage: 32Gi, while the pod keeps running.

> *On screen:* A `kubectl patch pvc … 32Gi` command appears while the pod box stays running.

Because the class has `allowVolumeExpansion: true`, growing the disk is just a PVC edit: `kubectl patch pvc data-catalog-mysql-ebs-0 -p '{"spec":{"resources":{"requests":{"storage":"32Gi"}}}}'`. The pod keeps running throughout. The PVC moves through `Resizing` and then `FileSystemResizePending` conditions, visible in `kubectl describe pvc`.

**[02:57]** Two stages: the cloud volume grows, then the filesystem. Grow only, never shrink.

> *On screen:* Two boxes draw in, `1. csi-resizer: EBS ModifyVolume` → `2. node plugin: grow ext4 online`, with `about 83 s, restarts: 0` beside them.

Expansion happens in two stages. First, `csi-resizer` calls `ModifyVolume` and the EBS volume grows (the AWS modification goes `modifying` → `optimizing`). Then the node plugin grows the ext4 file system while it is mounted. Live it took about 83 s (09:23:23 → 09:24:46), `df` showed 32G and the pod restarted 0 times [LIVE]. You can only grow a PVC; shrinking is not possible.

**[03:01]** Deleting the StatefulSet is safe; deleting the PVC deletes the disk.

> *On screen:* Two result rows appear: green `delete StatefulSet` (PVC and disk kept) and red `delete PVC` (PV and EBS volume deleted within ~10 s).

The StatefulSet's `persistentVolumeClaimRetentionPolicy` was `whenDeleted: Retain`. Deleting the StatefulSet detached the volume within ~15 s but kept the PVC and the disk, and re-applying it re-attached the same disk, so `test.txt` still read 123. Deleting the PVC is different: with `reclaimPolicy: Delete`, the PV and the EBS volume were gone within 10 s and 0 tagged volumes remained [LIVE]. Deleting a namespace deletes its PVCs too, so check `kubectl get pv` first.

### Key takeaways  `[03:06]`

- StatefulSet: stable names and one PVC per replica
- WaitForFirstConsumer creates the disk in the pod's AZ
- EBS is one AZ, one node: plan nodes in every AZ
- Expand online; PVC delete with Delete policy is permanent

---

## Chapter 3 — Amazon EFS: shared storage

**Starts at 03:20** · length 01:25 · source `S03-efs` · hook: *"How can many pods in many AZs share the same files?"*

**What you'll learn.** This chapter follows `concepts/storage/02-efs/` (`01-existing-architecture.md`, `02-efs-csi-driver.md`, `03-dynamic-provisioning-using-efs.md`) and `labs/03-storage-efs.md`. It shows why the `ui` service needs shared storage, how an EFS file system reaches every AZ through mount targets, and how the CSI driver provisions one access point per claim. All results are [LIVE]: claim bound in under 1 s, pods in three AZs sharing one folder, and a real lost-writes concurrency result. Watch Chapter 2 first; the EBS vs EFS contrast is the point.

### The problem: images baked into every ui pod

**[03:27]** Product images are bundled into the container at build time.

> *On screen:* Several `ui pod` boxes appear, each carrying its own `images (in image)` block.

The retail store's `ui` service serves product images that are baked into the container image at build time [W]. Before the lab, `kubectl describe deployment -n ui` showed only an in-memory `emptyDir` mounted at `/tmp` [LIVE]. Each replica therefore carries a private copy of the images.

**[03:30]** So nothing can be added at run time, and nothing is shared.

> *On screen:* A box `new image? rebuild every pod` appears under the pods.

Adding a single product photo would mean rebuilding and redeploying the image, and nothing written by one replica is visible to another. The workshop's fix is to put the images on a shared Amazon EFS volume that every `ui` pod mounts [W].

### EFS: one regional file system, a mount target per AZ

**[03:35]** Each mount target is a network endpoint (ENI) in one AZ; clients use their own AZ's.

> *On screen:* A regional frame holds the EFS file system at the top and three AZ boxes below, each with a mount target and its IP, linked up to the file system.

EFS is a regional, serverless NFS file system with no size to choose. A pod's `df` reported `8.0E` (8 exabytes) because there is no fixed capacity [LIVE]. Clients reach it through **mount targets**, one network endpoint (ENI with an IP) per AZ, and each node uses the mount target in its own AZ. The pre-built `eks-workshop-efs-assets` file system had mount targets in us-west-2a, 2b and 2c [LIVE]; if an AZ had none, nodes there could not mount [BG].

**[03:40]** Must exist first: the file system, mount targets, and an SG allowing port 2049.

> *On screen:* A security-group bar appears at the bottom: allow NFS TCP 2049 from the VPC.

Three things must exist before pods can mount EFS: the file system, a mount target in each AZ your nodes use, and a security group on the mount targets that allows NFS (TCP 2049) from the nodes. In the lab the rule allowed the whole VPC CIDR 10.42.0.0/16 [LIVE]. A wrong rule shows up as pods stuck in `ContainerCreating` with mount timeouts, the most common EFS problem [BG]. The workshop's `prepare-environment` creates all three for you.

### EBS vs EFS at a glance

**[03:48]** EBS is for databases; EFS is for content many pods share.

> *On screen:* An EBS-vs-EFS comparison table fills in row by row: type, sharing, AZ scope, capacity, attach step, Fargate, use case.

EBS is a block disk: one AZ, one node at a time (RWO), a size you choose, a real attach step, EC2 only, lowest latency, so ideal for databases. EFS is NFS 4.1: many nodes at once (RWX), all AZs, elastic capacity billed per GB stored, no attach step, Fargate supported, higher latency. Typical EFS uses are shared content, CMS assets, ML datasets and home directories [W/BG].

### The EFS CSI driver hands out folders, not disks

**[03:54]** efs-ap: make one EFS access point per PersistentVolume.

> *On screen:* Add-on boxes show `aws-efs-csi-driver ACTIVE in 34 s` and `only csi-provisioner`, next to the `efs-sc` StorageClass with `provisioningMode: efs-ap`.

The EFS add-on went `CREATING` → `ACTIVE` in 34 s (v3.5.2-eksbuild.1) [LIVE]. Compared with EBS it has no csi-attacher (nothing to attach) and no csi-resizer (EFS has no size); the only sidecar is `csi-provisioner`. Its StorageClass `efs-sc` sets `provisioningMode: efs-ap`, the `fileSystemId` (injected with `envsubst`) and `directoryPerms: "700"`. The IAM role trusts both the controller and the node ServiceAccounts, because the node's mount helper also uses credentials [BG].

**[03:57]** Live: the claim was provisioned in under a second; volumeHandle = fs-id::fsap-id.

> *On screen:* A PVC box `efs-claim RWX · 5Gi (ignored)` points to an access-point box with its root path and uid/gid 50000, with `under 1 s` over the arrow.

An **access point** is an EFS entry point with a fixed root directory and a forced POSIX identity. The driver creates one per PVC, giving each app its own folder in a shared file system. Live: the claim was provisioned at 09:33:35 → 09:33:36, under a second. The PV's `volumeHandle` was `fs-0681…::fsap-0532…` (file system ID plus access point ID), with root `/pvc-837af927-…`, uid/gid 50000 and permissions 700 [LIVE]. The 5Gi request is required by the API, but EFS ignores it.

**[04:01]** Immediate binding is fine: there is no AZ lock and no node affinity.

> *On screen:* The caption appears over the same diagram: Immediate binding, no AZ lock, no node affinity.

`efs-sc` uses `volumeBindingMode: Immediate`, so the claim is provisioned before any pod exists. That is safe because an NFS file system is reachable from every AZ: the PV has no `nodeAffinity` and there is no `VolumeAttachment`. One pod briefly logged `pod has unbound immediate PersistentVolumeClaims` for about a second before the PV appeared, which is harmless [LIVE].

### Three pods, three AZs, one folder

**[04:06]** The two ui pods landed in us-west-2b and 2c and mounted the same claim.

> *On screen:* Three `ui` pod boxes in different AZs each show `/efs` and connect up to one shared access point.

The `ui` Deployment was patched to 2 replicas, with volume `efsvolume` from `efs-claim` mounted at `/efs` and `RETAIL_UI_PRODUCT_IMAGES_PATH=/efs` [W]. The two pods landed in us-west-2b and us-west-2c and mounted the same claim [LIVE]. Inside a pod the mount source is `127.0.0.1` on a local port, because the EFS mount helper runs a small TLS proxy on each node and encrypts traffic in transit [LIVE mount; BG mechanism].

**[04:09]** A Job unzipped 12 images into the volume; both pods saw them at once.

> *On screen:* A `Job populate-images, 12 .jpg files` box appears beside the access point with an arrow into it.

A Kubernetes Job mounted the same claim at `/storage`, downloaded `sample-images.zip` from the retail-store release, unzipped 12 `.jpg` files and exited. Both `ui` pods listed the 12 files immediately [LIVE]. The Job needed no special setup; it simply mounted the claim. That is what shared storage means in practice.

**[04:11]** Scaled to 3: the new pod in us-west-2a listed the same files.

> *On screen:* The third pod in us-west-2a lights up showing the same files.

Scaling `ui` to 3 replicas placed the new pod in us-west-2a, and all three pods listed the same 14 files [LIVE]. The volume is regional and each node mounts through the mount target in its own AZ. Deleting a `ui` pod changed nothing, because the data lives in EFS, not in the pod.

**[04:13]** A file added after deployment was served over the NLB: 200 image/jpeg.

> *On screen:* A note types in at the bottom: pods run as uid 1000, files are owned by 50000:50000, and the access point maps every request.

Pod 1 downloaded `placeholder.jpg` (4824 B) into `/efs`, and fetching it through the NLB returned `200 image/jpeg 4824B`. The running app served a file added *after* deployment [LIVE]. The app runs as uid 1000, but the files belong to 50000; it can still read and write because the access point forces every request to 50000, so no `chown` is ever needed. (The `ui` image has no `wget`; use `curl`.)

### RWX is not 'multi-writer safe'

**[04:19]** Two pods appended at the same time: 2 lines lost in one live run.

> *On screen:* Pod A (AZ b) and pod B (AZ c) both draw arrows into `shared.log`, and a result box shows `8 lines (expected 10)`.

Two pods in different AZs each appended 5 lines to the same file at the same time. The file ended with 8 lines, so 2 were lost in that single run [LIVE]. NFS gives you a shared *file system*, not safe concurrent appends from several clients without coordination. Results vary from run to run [BG].

**[04:24]** NFS shares a file system; coordinating writers is your job.

> *On screen:* A remedies line types in: one file per writer, file locks (flock), or a real database or queue.

`ReadWriteMany` means many nodes may mount the volume read-write. It does not mean many writers are automatically safe. Remedies: give each writer its own file, use file locking (`flock` works over NFS 4), or keep shared mutable state in a database or queue. EFS suits read-mostly shared content like the product images.

**[04:26]** The driver deletes what it created: the access point, never the file system.

> *On screen:* A box summarises deletion: an in-use claim waits in Terminating, then the PV and access point go, while the file system and mount targets stay.

`kubectl delete pvc efs-claim` while pods used it left the PVC `Terminating`, held by the `kubernetes.io/pvc-protection` finalizer. It stayed for about two more minutes even after `ui` stopped using it; once the completed `populate-images` Job was deleted, the PVC, PV and access point were gone within ~30 s. The source treats the Job as the *probable* holder, not proven [LIVE]. The EFS file system and its mount targets stayed `available`: `reclaimPolicy: Delete` removes only what the driver created, the access point.

### Key takeaways  `[04:32]`

- EFS = regional NFS, mounted from every AZ (RWX)
- Needs mount targets per AZ and an SG allowing 2049
- efs-ap: one access point (folder + uid) per PVC, <1 s
- Shared is not concurrency-safe: coordinate writers

---

## Chapter 4 — Mountpoint for Amazon S3

**Starts at 04:46** · length 01:31 · source `S04-mountpoint-s3` · hook: *"Can a pod read an S3 bucket as if it were a folder?"*

**What you'll learn.** This chapter follows `concepts/storage/03-mountpoint-s3/` (`01-existing-architecture.md`, `02-mountpoint-s3-csi-driver.md`, `03-persistent-object-storage-with-s3.md`) and `labs/04-storage-mountpoint-s3.md`. It explains S3's object model, how Mountpoint translates file calls into S3 requests, the v2 driver's per-node Mountpoint pods, the static PV, and the hard limits (no append, overwrite or rename). All runs are [LIVE]: add-on ACTIVE in 23 s, a CLI upload visible in a pod after 1 s, and 16 objects still in the bucket after the PVC and PV were deleted.

### S3 stores objects, not files

**[04:53]** An object is whole data plus metadata, addressed by a key.

> *On screen:* A bucket frame fills with object boxes, each labelled `key: …`.

S3 is object storage. A **bucket** is a named container in one region, and an **object** is a whole piece of data plus metadata, addressed by a **key**. New buckets are private by default: the lab bucket came with all four Block Public Access settings on and default SSE-S3 (AES256) encryption [LIVE].

**[04:56]** There are no real folders: mkdir folder1 only produced the key folder1/inner.txt.

> *On screen:* A side note types in: `folder1/` is only a prefix of the key, there is no folder object.

Folders in S3 are an illusion. After `mkdir folder1` and writing `inner.txt` through the mount, the bucket held only the single key `folder1/inner.txt`; no folder object was created [LIVE]. Tools display prefixes as folders, but nothing about a "directory" exists on its own.

**[04:59]** Objects are immutable: to change one byte you replace the whole object.

> *On screen:* A second note appears: objects are written whole, with no editing bytes in the middle.

Objects are immutable. There is no API to change byte 100 of an object or append to it; you upload a new object that replaces the old one. That single fact explains every Mountpoint limit at the end of this chapter.

### Mountpoint: file calls in, S3 API calls out

**[05:06]** It translates file calls into S3 API calls (*rm was not tested live).

> *On screen:* Three columns, `ui pod`, `Mountpoint (FUSE)` and `Amazon S3`, are linked by arrows mapping `ls`, `open/read`, `write a NEW file` and `rm*` to S3 requests.

Mountpoint for Amazon S3 is a FUSE file client: the container makes ordinary file calls and Mountpoint turns them into S3 requests [W]. The mapping shown (`ls` → list, `open/read` → GetObject, new file → PutObject, `rm` → DeleteObject) is a general illustration, not taken from the lab. The source names only the IAM actions. The `rm` row is starred because the in-pod delete test was not run live.

**[05:10]** Least privilege: the IAM policy is a hard ceiling for what the mount can do.

> *On screen:* An IAM banner appears: role for `kube-system:s3-csi-driver-sa`, scoped to ONE bucket, listing the allowed actions.

The workshop's Terraform creates a role for ServiceAccount `kube-system:s3-csi-driver-sa` covering only this bucket: `s3:ListBucket` on the bucket, plus `GetObject`, `PutObject`, `AbortMultipartUpload` and `DeleteObject` on `bucket/*` [W/LIVE]. The IAM policy is a hard ceiling: the PV's `allow-delete` option does nothing if the role lacks `s3:DeleteObject`. Clusters with several buckets give each volume its own credentials or role [BG].

### Driver v2: a Mountpoint pod per volume per node

**[05:19]** When a consumer pod starts, the driver creates a Mountpoint pod in namespace mount-s3.

> *On screen:* An add-on banner `ACTIVE in 23 s (v2.8.0)` sits above two node boxes, each holding a `ui pod`, an `mp-…` Mountpoint pod in ns `mount-s3`, and the `s3-csi-node` DaemonSet.

`aws-mountpoint-s3-csi-driver` went `ACTIVE` in 23 s, creating the `s3-csi-node` DaemonSet (3 pods), an `s3-csi-controller`, and a new namespace `mount-s3` [LIVE]. In driver v2, when the first consuming pod starts on a node, the driver creates a dedicated Mountpoint pod for that volume on that node. Live, `mp-n8qlg` and `mp-9spzj` appeared in the same second the `ui` pods were scheduled. The CSIDriver has `attachRequired: false`, so there is no VolumeAttachment.

**[05:23]** The FUSE process is visible in kubectl; it went away ~8 s after the last consumer left.

> *On screen:* The caption appears over the same two-node diagram.

Running the FUSE process in its own pod makes it visible in `kubectl`, gives it resource accounting, and lets it survive node-plugin restarts [BG]. When the last consumer left, the Mountpoint pods were removed within about 8 s [LIVE]. If a mount fails, check both the `s3-plugin` logs in the node DaemonSet and the Mountpoint pod's logs in `mount-s3`.

### Static provisioning: point a PV at the bucket

**[05:32]** No disk to create: an empty storageClassName means no dynamic provisioning.

> *On screen:* A large `PersistentVolume s3-pv` card with its mount options appears, then a `PVC s3-claim` card binds to it.

There is no disk to create, so the lab uses **static** provisioning [W]. The PV names the driver (`s3.csi.aws.com`), any unique `volumeHandle`, the `bucketName`, `ReadWriteMany`, and mount options `allow-delete`, `allow-other`, `uid=1000`, `gid=1000`, `region=us-west-2`. Its 1Gi capacity is required by the API and meaningless for S3. The PVC sets `storageClassName: ""` (empty means no dynamic provisioning) and `volumeName: s3-pv`.

**[05:36]** The PVC binds to exactly that PV; uid/gid options invent owners S3 doesn't have.

> *On screen:* A result box appears under the PVC: Bound immediately, reclaimPolicy Retain, files show as 1000:1000.

At 09:43:17 the PV bound to `ui/s3-claim` immediately, with no provisioning step [LIVE]. Inside a `ui` pod the mount showed as `fuse` with size 8.0E, and every file appeared as `rw-rw----` owned by 1000:1000. S3 has no Unix owners, so the `uid`/`gid` options invent them. The PV's `reclaimPolicy` is `Retain`, so deleting the claim never touches the bucket.

### Write in one pod, see it everywhere

**[05:42]** Pod 1 curls placeholder.jpg into /mountpoint-s3...

> *On screen:* Two pod boxes face an S3 bucket box; a `placeholder.jpg` card slides from pod 1 toward the bucket.

The workshop writes through the mount: `kubectl exec $POD1 -n ui -- curl -sS -o /mountpoint-s3/placeholder.jpg 'https://placehold.co/…'`. Creating a new file with a sequential write is exactly what Mountpoint supports: it uploads the object when the file is closed [BG for timing].

**[05:45]** ...it becomes a real S3 object, and pod 2 sees 13 files.

> *On screen:* The file appears in the bucket with its metadata, and an arrow carries it to pod 2, now showing 13 files.

Pod 2 listed 13 files, and `aws s3 ls` showed `placeholder.jpg` as a real object: 4824 bytes, SSE AES256, content type `binary/octet-stream`, ETag ending `-1` because it was uploaded as a single-part multipart upload [LIVE]. The content type is generic because Mountpoint does not guess MIME types, which matters if the bucket also serves browsers directly.

**[05:47]** The other way works too: a CLI upload showed up in the pod 1 second later.

> *On screen:* A CLI box appears below the bucket: `aws s3 cp from-cli.txt` became visible in the pod after 1 s.

In the other direction, `from-cli.txt` uploaded with `aws s3 cp` could be read in the pod 1 second later [LIVE]. By default Mountpoint does not hide new objects behind a long metadata cache. Caching options can cut request costs, but they trade away that freshness [BG].

### The limits: S3 is not a POSIX file system

**[05:55]** Read anything, write new objects once, list, optionally delete. Nothing else.

> *On screen:* A table of seven file operations fills in, each with a green OK or red NO and the exact error message.

The limits were tested live on `/mountpoint-s3`. Creating a new file and reading it back worked, and so did `mkdir` plus writing inside it. Append (`>>`), overwrite (`>`) and `chmod` failed with `Operation not permitted`, `mv` with `Function not implemented`, and a random write with `dd seek=100` with `Invalid argument` [LIVE]. Mountpoint supports only what maps cleanly onto S3: read anything, write new objects once, list, and optionally delete.

**[05:59]** Databases, appending logs, SQLite, rename-into-place: use EBS or EFS instead.

> *On screen:* The caption appears beside the limits table.

Anything that edits files in place is the wrong fit: databases, append-only logs, SQLite, and tools that rename a temp file into place. Use EBS or EFS for those, or S3 Files (next chapter) when you need full POSIX on S3-backed data. Newer options such as `allow-overwrite` exist [BG], but they were not enabled here.

**[06:02]** Deleting the Kubernetes objects never touches the bucket's data.

> *On screen:* A final bar appears: after deleting the PVC and PV, all 16 objects were still in the bucket.

Teardown: restoring `ui` removed the two Mountpoint pods within ~8 s, and `kubectl delete pvc s3-claim` left the PV `Released` (reclaim `Retain`), so it was deleted by hand. All 16 objects stayed in the bucket: the 12 originals, the placeholder and 3 test files [LIVE]. Emptying and deleting the bucket is a separate step, and costs money until you do it. Mountpoint also bills per request, so a chatty app doing many small `stat`/`list` calls costs more than large sequential reads [BG].

### Key takeaways  `[06:05]`

- Mountpoint turns file calls into S3 API calls
- v2 runs one Mountpoint pod per volume per node
- Static PV + PVC with storageClassName ""
- Read and write-new only: no append, rename, chmod

---

## Chapter 5 — Amazon S3 Files

**Starts at 06:18** · length 01:12 · source `S05-s3-files` · hook: *"A real NFS file system that stays in sync with an S3 bucket"*

**What you'll learn.** Amazon S3 Files gives pods a real POSIX file system whose contents are kept in sync with a versioned S3 bucket. The chapter follows `concepts/storage/04-s3-files/` in order (01-existing-architecture → 02-s3-files-csi-driver → 03-static-vs-dynamic-provisioning → 04-static-provisioning-using-s3-files) and `labs/05-storage-s3-files.md`. It was executed live: every timing shown, such as the ≈57 s file-system-to-S3 sync and the 2 s reverse sync, is [LIVE]. It builds on the EFS and Mountpoint chapters, because S3 Files reuses the EFS CSI driver and is compared directly with Mountpoint.

### What S3 Files is

**[06:25]** Pods get full file semantics; the data also lives as ordinary S3 objects.

> *On screen:* A bucket and a file system appear side by side, with sync arrows running between them and pods mounting the file system.

S3 Files is an NFS file system (built on EFS technology) attached to a **versioned** S3 bucket. Pods see ordinary files and directories with full POSIX behaviour, while the same data is stored as S3 objects: POSIX attributes such as owner travel as object metadata, and directories become marker objects. So applications that need real file operations and systems that read the bucket can share one dataset.

**[06:30]** Mount targets in each AZ; the pods mount the file system over NFS port 2049.

> *On screen:* Mount targets drop into each Availability Zone, and pod arrows connect to them on NFS port 2049.

Like EFS, the file system is reached through a **mount target** (a network interface) in each AZ's subnet, guarded by a security group that must allow NFS on TCP 2049 from the nodes. [LIVE] the pod saw the mount as **NFS 4.2**. Because there is a target in every AZ, pods anywhere in the cluster can mount the same file system.

### Mountpoint vs S3 Files (tested live)

**[06:37]** Mountpoint can only write new files. S3 Files is a real POSIX file system.

> *On screen:* A comparison table fills in row by row: append, overwrite, rename and chmod get ticks for S3 Files and crosses for Mountpoint.

Mountpoint for S3 (previous chapter) translates file calls into S3 requests through FUSE, so it can only create **new** files; appending, overwriting, renaming or chmod fail. [LIVE] S3 Files supported append, overwrite, rename and chmod, because it really is a file system that syncs to the bucket afterwards. The trade-off is a **visibility lag** between the two sides (seconds to about a minute), where Mountpoint has none because it *is* S3.

### AWS pieces before Kubernetes

**[06:45]** The mount targets stayed 'creating' for about 5 minutes. Plan for that wait.

> *On screen:* The AWS building blocks stack up (bucket with versioning, file system, mount targets, security group, service role) and a clock shows the mount-target wait.

Before any Kubernetes object, you need a versioned bucket, the S3 Files file system (`aws s3files create-file-system --bucket … --role-arn …`), a service role trusted by `elasticfilesystem.amazonaws.com`, an NFS security group, mount targets, and client permissions for the nodes. [LIVE] the file system went from `creating` to `available` in **14 s**, but the three mount targets stayed `creating` for **about 5 minutes** (09:50:40 → 09:55:37). Wait for them to be available, or the pod mount will fail.

### Why only static provisioning works

**[06:51]** The EFS API can't see an S3 Files file system, so the PVC stays Pending.

> *On screen:* A dynamic PVC is drawn waiting in Pending, with the error "File System does not exist" popping up beside the EFS API.

S3 Files uses the **EFS CSI driver (≥ 3.0.0)**, but dynamic provisioning (`provisioningMode: efs-ap`) asks the EFS API to create an access point, and the EFS API cannot see an S3 Files file system. [LIVE] the PVC stayed `Pending` with "File System does not exist". The fix is static provisioning: you create the file system yourself and write a PV that points at it.

**[06:55]** The PV points at the file system; NFS ignores fsGroup, so an init container chowns.

> *On screen:* A static PV card appears with `volumeHandle: s3files:<fs-id>`, then an init container runs `chown` on the mount before the app container starts.

The static PV uses `csi.driver: efs.csi.aws.com` with `volumeHandle: s3files:<fs-id>`, and the PVC binds to it straight away. [LIVE] the PVC showed `Pending` for 2 s while the binder ran. The app runs as uid 1000 but the volume root is owned by root, and on NFS the pod's `fsGroup` does not change ownership, so the lab adds an init container that `chown`s the directory. Without it the app gets `Permission denied`.

### Two-way sync is not symmetric (measured)

**[07:02]** A pod's new files reached S3 after about a minute.

> *On screen:* Files written by a pod travel along the file-system-to-S3 arrow while a timer counts up to about 57 s.

[LIVE] a Job wrote 12 files into the file system: the first objects appeared in the bucket after **≈57 s**, and all 12 of 12 by **≈69 s**. A small text file also took about a minute. The file system is the side you write to quickly; export to S3 is asynchronous, in batches.

**[07:06]** Changes in the bucket show up in the file system within seconds.

> *On screen:* The reverse arrow lights up: an object uploaded to the bucket appears in the pod's directory within 2 s, and a delete within 8 s.

[LIVE] `aws s3 cp` of a new object was visible in the pod after **2 s**, an overwrite (a new object version) after **2 s**, and an `aws s3 rm` made the file disappear within **8 s**. Because the bucket is versioned, after upload, overwrite and delete the bucket held **2 versions + 1 delete marker** for that key. Clean those up before deleting the bucket.

**[07:10]** Design for the lag: another system reading the bucket won't see a write instantly.

> *On screen:* A second system reading the bucket is drawn with a delay marker between the pod's write and the object appearing.

Design for asymmetric, eventual sync: a pod's write is not instantly visible to Lambda functions or analytics jobs reading the bucket. If both sides can change the same file at about the same time, the service applies a conflict policy; read its documentation before using it for concurrent writers [BG]. With `Retain` and static provisioning, deleting the PVC/PV leaves the file system and bucket in place, and you remove them yourself.

### Key takeaways  `[07:16]`

- Real NFS file system, synced with a versioned S3 bucket
- Same EFS CSI driver; volumeHandle s3files:<fs-id>
- Static provisioning only; chown with an init container
- S3 → FS in seconds, FS → S3 up to about a minute

---

## Chapter 6 — Amazon FSx for OpenZFS

**Starts at 07:31** · length 01:14 · source `S06-fsx-openzfs` · hook: *"One PVC = one child volume inside a managed ZFS file system"*

**What you'll learn.** Amazon FSx for OpenZFS is a managed ZFS file system served over NFS. Kubernetes uses it by carving one child volume per PVC out of a file system you size up front. The chapter follows `concepts/storage/05-fsx-openzfs/` (01-existing-architecture → 02-fsx-openzfs-csi-driver → 03-dynamic-provisioning-using-fsx-openzfs) and `labs/06-storage-fsx-openzfs.md`. It was executed live, including two surprises found on the cluster: the PVC size was not enforced, and compression made `df` misleading. Compare it with EFS from chapter 3, which uses the same "one claim = one sub-unit" idea.

### A file system you size, volumes you carve out

**[07:37]** The lab file system is sized up front: 128 GiB of SSD, 160 MB/s, in one AZ.

> *On screen:* A file-system box is drawn with its capacity and throughput labels and pinned to a single AZ.

Unlike EFS, which grows elastically, FSx for OpenZFS makes you choose capacity and throughput when you create it. [LIVE] the lab file system was `SINGLE_AZ_2` with **128 GiB SSD** and **160 MB/s**, created via `aws fsx create-file-system` (FileSystemType OPENZFS). It is EC2-only (no Fargate) and lives in one AZ, though pods in other AZs can still mount it.

**[07:44]** Each claim becomes a child volume under /fsx: fast, with its own settings.

> *On screen:* Child volumes peel off the root volume under `/fsx`, one per claim, each with its own small settings card.

The dynamic StorageClass does not create a new file system per PVC. It creates a **child volume** under the root volume, set by `ResourceType: volume` and `ParentVolumeId: <root volume id>` in the StorageClass. Each volume can carry its own NFS export rules, compression and record size. So one file system serves many claims, each isolated in its own directory tree.

### The CSI driver is installed with Helm

**[07:49]** Not an EKS add-on here. Controller and node plugin were ready in 16 seconds.

> *On screen:* A Helm chart box installs the controller and node plugin, and a ready check appears at 16 s.

For OpenZFS the CSI driver comes from Helm (`aws-fsx-openzfs-csi-driver`), not as an EKS add-on. The controller ServiceAccount is annotated with an IRSA role (`AmazonFSxFullAccess` in the workshop). [LIVE] the controller (provisioner, snapshotter and resizer sidecars) and the node DaemonSet were ready in **16 s**. Check both are Running before applying the StorageClass.

**[07:56]** The StorageClass tells the driver to make a volume under the root volume.

> *On screen:* The StorageClass YAML appears and its key parameters are highlighted one by one.

The key parameters are `ResourceType: volume`, `ParentVolumeId` (exported as `ROOT_VOL_ID` from `describe-file-systems`), NFS export options, compression, and `OptionsOnDeletion: DELETE_CHILD_VOLUMES_AND_SNAPSHOTS`. [LIVE] binding was `Immediate` and `reclaimPolicy: Delete`. Volume expansion was not allowed by this class, even though the driver supports resizing. The mount options use NFS 4.2, 1 MiB read/write sizes and `nconnect=16`, which opens 16 parallel TCP connections per mount for throughput [BG].

### One PVC → one FSx volume, in 76 seconds

**[08:01]** The driver asks the FSx control plane for a volume and waits until it is AVAILABLE.

> *On screen:* A timeline runs from PVC created at 0 s, through repeating "waiting for a volume" events every ~15 s, to ProvisioningSucceeded at 76 s.

[LIVE] the PVC was created at 10:14:19, the external provisioner logged "waiting for a volume" roughly every 15 s, and `ProvisioningSucceeded` arrived at 10:15:34, about **76 s** later. The driver asks the FSx control plane to create the volume and waits until it is `AVAILABLE`. Budget 1–2 minutes per new claim, so this class suits long-lived volumes rather than throw-away ones.

**[08:06]** Pods mount it directly by NFS 4.2 from any AZ. No attach, no node affinity.

> *On screen:* Pods in different AZs draw NFS arrows straight to the file system's DNS name, with no attach step shown.

There is no EBS-style attach: the node mounts the file system's DNS name over NFS 4.2, and the PV has no node affinity, so pods can run in any AZ. [LIVE] pods outside the file system's AZ mounted it fine. The trade-offs are cross-AZ latency, data-transfer cost, and dependence on that one AZ being healthy.

**[08:10]** EFS made an access point in under 1 s; OpenZFS takes about 1–2 minutes per claim.

> *On screen:* Two bars compare provisioning time per claim: EFS under 1 s against OpenZFS at about 76 s.

Both drivers create a sub-unit per claim: an EFS **access point** versus an OpenZFS **child volume**. Creating an access point is a metadata operation, so [LIVE] EFS bound in under 1 s, while an OpenZFS volume is real storage the FSx service must create (≈76 s). Pick OpenZFS for its low latency and ZFS features (snapshots, compression), not for fast claim creation.

### Two surprises found live

**[08:17]** The PVC size is not enforced here. Real limits need quota parameters.

> *On screen:* A 1Gi request label is shown while a 1.2 GiB write bar overflows it without any error.

[LIVE] the PVC asked for `1Gi`, yet `dd bs=1M count=1200` wrote **1.2 GiB** with no error. The child volume's quota was the file system's whole **128 GiB** (`StorageCapacityQuotaGiB` 128), so `requests.storage` alone does nothing here. For a real per-claim limit, use the driver's quota/reservation parameters [BG: check the driver docs], or one tenant can fill the whole file system.

**[08:22]** Compression makes /dev/zero benchmarks misleading: df counts compressed bytes.

> *On screen:* A 1.2 GiB stack of zeros shrinks into a tiny 2.0M block on the `df` gauge.

The file system uses LZ4 compression, so the 1.2 GiB of zeros from `/dev/zero` collapsed and [LIVE] `df` reported only **2.0M used**. The same effect made `dd` look like ~757 MB/s, which is not a valid benchmark. Real data compresses less; billing and `df` both count *compressed* bytes. Benchmark with incompressible (random) data.

### Deleting the claim

**[08:26]** reclaimPolicy Delete removes the child volume; the file system stays yours to delete.

> *On screen:* Deleting the PVC removes the child volume (status DELETING) while the root volume and file system stay drawn in place.

[LIVE] `kubectl delete pvc fsxz-claim` at 10:17:04 removed the PV within 2 s and set the FSx volume to `DELETING`. `reclaimPolicy: Delete` plus `DELETE_CHILD_VOLUMES_AND_SNAPSHOTS` let the driver delete only what it created. The **file system and root volume remain** and keep billing until you run `aws fsx delete-file-system` yourself.

### Key takeaways  `[08:32]`

- Managed ZFS over NFS; you size capacity and throughput
- Helm driver; StorageClass ResourceType: volume
- One PVC = one child volume, about 76 s to provision
- Claim size not enforced; LZ4 hides real usage

---

## Chapter 7 — Amazon FSx for Lustre

**Starts at 08:45** · length 01:13 · source `S07-fsx-lustre` · hook: *"A parallel file system built for throughput: ML, HPC, media"*

**What you'll learn.** Amazon FSx for Lustre is a parallel file system for throughput-heavy work such as ML training and HPC. Pods mount it with the Lustre client instead of NFS. The chapter follows `concepts/storage/06-fsx-lustre/` (01-existing-architecture → 02-fsx-lustre-csi-driver → 03-dynamic-provisioning-using-fsx-lustre) and `labs/07-storage-fsx-lustre.md`. It was executed live with a pre-created file system and a **static** PV, including a verified cross-pod file-locking test. The single-pod throughput numbers are indicative only.

### Parallel, not NFS

**[08:52]** Many clients pull different pieces at the same time: very high parallel throughput.

> *On screen:* Data is striped across several storage servers, and many clients pull different stripes in parallel arrows at once.

Lustre splits files across many storage servers, so a large number of clients can read or write different pieces at the same time, and aggregate throughput grows with the file system. That is why it suits jobs such as many training pods reading one dataset. Single-client latency is not its selling point; parallel throughput is. Like the other FSx services, it is EC2-only (no Fargate).

**[08:55]** Pods mount it with the Lustre client over LNet, not over NFS.

> *On screen:* The mount arrow is relabelled from NFS to Lustre/LNet as it connects the pod to the file system.

Instead of NFS, the node uses the Lustre kernel client over **LNet**. [LIVE] the mount showed filesystem type `lustre` with a source like `<ip>@tcp:/<mountname>`, where `@tcp` means "LNet over TCP" and the IP is one of the file system's network interfaces. The mount options included `flock` (from the PV) and `checksum`. `df` showed the true capacity, **1.2T**.

### Deployment types and the lab's file system

**[09:01]** Scratch for temporary processing, persistent for longer-term data.

> *On screen:* Two deployment-type cards appear: SCRATCH, marked temporary and unreplicated, and PERSISTENT, marked long-term.

SCRATCH file systems are for temporary processing: data is not replicated, so a server failure can lose it. PERSISTENT file systems replicate data for longer-lived workloads. [LIVE] the lab used `PERSISTENT_2`, **1200 GiB** SSD (the minimum size), **125 MB/s per TiB** (≈150 MB/s baseline) and LZ4 compression. Lustre can also link to an S3 bucket as a data repository [W], but this lab did not use it.

**[09:04]** It took roughly 5 to 9 minutes to build, so the lab mounts a pre-created one.

> *On screen:* A build clock spins for 5 to 9 minutes beside the file system, then a pre-created badge is stamped on it.

[LIVE] the file system was created at 10:08:41, was still `CREATING` at 10:13:32 and `AVAILABLE` by 10:17, roughly **5–9 minutes**. That is too slow (and too expensive at a 1.2 TiB minimum) to create per PVC, so the lab mounts one pre-created file system through a static PV. A dynamic StorageClass (subnetId, securityGroupIds, deploymentType, perUnitStorageThroughput) would create a whole file system per claim [W].

### Security group first, then a static PV

**[09:10]** The security group must exist before the file system, or FSx rejects it.

> *On screen:* A security group with ports 988 and 1018–1023 is drawn first; the file system is then created behind it, with a red reject shown for the wrong order.

Lustre needs inbound **TCP 988** and **TCP 1018–1023** from the VPC. [LIVE] the lab's security group allowed exactly those from the VPC CIDR. The workshop's Terraform notes that if the rules do not exist when the file system is created, FSx rejects it with `InvalidNetworkSettings` (no LNet traffic on port 988) [W]. So create the security group and its rules first, then the file system.

**[09:15]** The PV holds the file system's DNS name and mount name. Lustre ignores fsGroup too.

> *On screen:* A static PV card appears with `volumeHandle`, `dnsname` and `mountname`, then an init container chowns the mount.

The driver is the EKS add-on `aws-fsx-csi-driver` with an IRSA role; [LIVE] the add-on was ACTIVE in 33 s. The static PV sets `volumeHandle: <fs-id>`, `volumeAttributes: {dnsname, mountname}` (read from `aws fsx describe-file-systems`), `mountOptions: [flock]` and `persistentVolumeReclaimPolicy: Retain`. As with NFS, the volume root is owned by root and `fsGroup` doesn't fix it, so an init container `chown`s it.

### Inside the pod: a real lustre mount with locking

**[09:21]** Two ui pods in other AZs both saw the same 12 files on the one-AZ file system.

> *On screen:* Two ui pods in two other AZs connect to the single-AZ file system, and both list the same 12 files.

[LIVE] the `populate-images` Job wrote 12 files, and both `ui` pods listed all 12, even though they ran in different AZs from the file system. Cross-AZ mounting works, with the usual latency and data-transfer cost. The PVC bound immediately because the PV already existed. One pod briefly logged `FailedScheduling "unbound immediate PersistentVolumeClaims"` for about 7 s while the binder ran.

**[09:29]** With the flock mount option, locks are enforced between clients. Verified live.

> *On screen:* A first pod takes an exclusive lock, a second pod's attempt shows LOCK-BUSY, then GOT-LOCK appears after the first releases it.

[LIVE] one pod ran `flock -x /fsxl/lockfile -c "sleep 12"`. A second, non-blocking locker got **LOCK-BUSY** while it was held and **GOT-LOCK** after release. Locks are enforced **between clients** because of the `flock` mount option; without it, `flock()` would only be local to each client [BG]. Many applications rely on file locks for correctness, so this option matters.

**[09:33]** One pod, 2 GiB: indicative only. Lustre shines with many clients in parallel.

> *On screen:* Write and read bars show 429 MB/s and 579 MB/s, with an "indicative only" stamp over them.

[LIVE] one pod wrote 2 GiB of incompressible data in 4.77 s (**≈429 MB/s**) and read it in 3.54 s (**≈579 MB/s**). The read was probably helped by the page cache, which couldn't be dropped inside the pod. Both exceed the ~150 MB/s baseline because `PERSISTENT_2` can burst and clients cache. Treat it as "works and is fast", not a benchmark; Lustre's real strength shows with many clients and files in parallel [BG].

### Teardown with a static PV

**[09:39]** A static PV never owns the file system. You delete it, or it keeps billing.

> *On screen:* Deleting the PVC leaves the PV in Released, it is deleted by hand, and the file system stays AVAILABLE until an explicit delete-file-system.

[LIVE] `kubectl delete pvc fsxl-claim` moved the PV `fsxl-pv` to **Released** (Retain), and it had to be deleted by hand along with the StorageClass. The **file system stayed `AVAILABLE`**, because a static PV never owns it, and was removed separately with `aws fsx delete-file-system`. Forgetting this step leaves a 1.2 TiB file system billing indefinitely.

### Key takeaways  `[09:45]`

- Parallel file system for throughput; EC2 only; 1.2 TiB minimum
- Security group (988, 1018-1023) before the file system
- Add-on driver + static PV: fs id, DNS name, mount name
- flock mount option makes locks work across pods

---

## Chapter 8 — FSx for NetApp ONTAP

**Starts at 09:59** · length 01:17 · source `S08-fsx-ontap` · hook: *"Trident turns each PVC into an ONTAP volume of exactly that size"*

**What you'll learn.** Amazon FSx for NetApp ONTAP brings NetApp's storage OS to AWS, and Kubernetes drives it through NetApp's **Trident** CSI driver instead of an AWS driver. The chapter follows `concepts/storage/07-fsx-ontap/` (01-existing-architecture → 02-fsx-ontap-csi-driver → 03-dynamic-provisioning-using-fsx-ontap), `labs/08-storage-fsx-netapp-ontap.md`, and the Trident finalizer story from `08-cleanup-process.md`. It was executed live: Pod Identity, the operator install, about 8 s provisioning and online expansion were all observed. So was the uninstall-order trap.

### File system → SVM → volumes

**[10:06]** Clients mount through the storage virtual machine, not the file system itself.

> *On screen:* A three-level hierarchy builds up: file system, then an SVM, then volumes, with the client arrow pointing at the SVM.

An ONTAP file system contains one or more **storage virtual machines (SVMs)**, and each SVM owns volumes and its own network endpoints. Clients mount through the **SVM's** address, not the file system's. [LIVE] the pod's NFS 4.2 mount pointed at the SVM, and Trident's backend config names the SVM it manages.

**[10:10]** Trident logs in with a secret. Creating the file system can take up to 30 minutes.

> *On screen:* A Secrets Manager secret key flows into Trident, and a long clock beside the file system shows up to 30 minutes.

Trident talks to ONTAP's own management API with admin credentials. In the lab they live in AWS Secrets Manager, and the backend config references the secret's ARN. The file system and SVM are created beforehand by the workshop's Terraform, because creation can take **up to ~30 minutes** [W]. A PVC never creates or deletes the file system itself.

### Identity: EKS Pod Identity (not IRSA)

**[10:16]** An association maps the ServiceAccount to an IAM role. No OIDC annotation.

> *On screen:* An association card links the `trident/trident-controller` ServiceAccount to an IAM role, with the IRSA annotation crossed out.

This lab uses **EKS Pod Identity** instead of IRSA: install the `eks-pod-identity-agent` add-on, create a role trusted by `pods.eks.amazonaws.com` (sts:AssumeRole + sts:TagSession), then `aws eks create-pod-identity-association --namespace trident --service-account trident-controller --role-arn <role>`. [LIVE] the agent DaemonSet was ACTIVE in 23 s. There is no ServiceAccount annotation and no OIDC provider; the policy was least-privilege, with Secrets Manager access limited to the one secret [W].

**[10:21]** The SDK in the controller fetches credentials from the node's link-local agent.

> *On screen:* The controller's SDK sends a credential request to the node-local agent at a link-local address, and temporary credentials flow back.

[LIVE] inside the controller pod, `AWS_CONTAINER_CREDENTIALS_FULL_URI=http://169.254.170.23/v1/credentials` was set. The AWS SDK calls the Pod Identity agent on its own node at that link-local address and receives role credentials. With IRSA the SDK instead exchanges a projected web-identity token via STS. If credentials fail, check the association exists and that the ServiceAccount name is exactly `trident-controller`.

### The operator pattern: a controller that creates controllers

**[10:26]** Unlike the AWS NFS drivers, Trident creates VolumeAttachment objects.

> *On screen:* The Helm-installed operator spawns a TridentOrchestrator, which then creates the controller and node pods, while VolumeAttachment objects appear beside them.

`helm install trident-operator` (chart 100.2410.0) installs an **operator**: a controller that reconciles a `TridentOrchestrator` and creates the real controller (6 containers) and the node pods. [LIVE] everything was Ready in ≈90 s, along with 16 CRDs. Trident's `CSIDriver` has `attachRequired=true`, so unlike the EFS and FSx NFS drivers it creates **VolumeAttachment** objects ([LIVE] `SuccessfulAttachVolume`).

**[10:30]** The backend tells Trident which SVM to manage. It must reach Bound and Success.

> *On screen:* A TridentBackendConfig card links Trident to the SVM, and its status turns to Bound / Success.

The `TridentBackendConfig` (driver `ontap-nas`, SVM name, file system ID, credentials = Secrets Manager ARN) tells Trident which storage to manage. [LIVE] `kubectl get tbc -n trident` showed **Bound / Success** with the message "Backend 'tbc-ontap-nas' created". If it shows Failed, check the secret, the credentials permissions and network reachability to the SVM before creating any PVCs. The StorageClass then uses provisioner `csi.trident.netapp.io` with `backendType: ontap-nas` and `allowVolumeExpansion: true`.

### PVC → ONTAP volume in about 8 seconds

**[10:38]** Trident calls ONTAP's own API, so the volume appears in seconds.

> *On screen:* A timeline marks kubectl apply, Provisioning, PVC Bound and VolumeAttachment, spanning about 8 seconds to Bound.

[LIVE] apply at 10:27:15, provisioning at 10:27:17, Trident `ProvisioningSuccess` at 10:27:23, and the PVC **Bound** at 10:27:24 (≈8 s). The VolumeAttachment followed at 10:27:31. That is far faster than OpenZFS (~76 s), because Trident calls ONTAP's API directly instead of going through the FSx control plane. One side effect: the volume isn't listed by the AWS FSx API, so use `kubectl get tridentvolume`.

**[10:41]** Unlike OpenZFS, the ONTAP volume has exactly the requested size, and grows online.

> *On screen:* Speed bars compare EFS, FSx ONTAP and FSx OpenZFS, then `df` shows 5.0G growing to 6.0G after a PVC patch.

Unlike OpenZFS, the ONTAP volume is created at **exactly** the requested size: [LIVE] `df` showed 5.0G for a 5Gi claim. Patching the PVC to `6Gi` took it through `Resizing`, and `df` showed **6.0G within ~3 s**, allowed because the class sets `allowVolumeExpansion: true`. Writing 5.5 GiB of zeros was inconclusive (`df` showed only 74M used, because ONTAP's storage efficiency collapsed the zeros), so the source does not claim the quota was enforced.

### The uninstall-order trap (hit live)

**[10:49]** Only the Trident controller removes that finalizer, and it was already gone.

> *On screen:* The trident namespace sits stuck in Terminating, while leftover objects carry a `trident.netapp.io` finalizer and the Trident controller is drawn already removed.

[LIVE] the Trident operator was uninstalled **before** its namespace, and `kubectl delete ns trident` hung in `Terminating`. `kubectl get ns trident -o json` showed 3 `tridentnodes` and 1 `tridentversion` still carrying the finalizer `trident.netapp.io`. Only the Trident controller removes that finalizer, and it no longer existed. The correct order is to delete backends and volumes, then the orchestrator, and only then the namespace.

**[10:53]** Never force a finalizer off a live resource: the AWS volume would leak and keep billing.

> *On screen:* A warning card shows that forcing a finalizer off a live volume leaks the AWS resource, with a billing meter still running.

The fix applied was safe only because Trident backends and volumes were already 0: the finalizers were cleared with `kubectl patch … -p '{"metadata":{"finalizers":null}}'`, and the namespace finished deleting. A finalizer exists to protect a cleanup step. Forcing it off an object that still owns a real volume or load balancer skips that step, so the cloud resource leaks and keeps billing. Always check what a finalizer protects before removing it.

### Key takeaways  `[11:02]`

- ONTAP hierarchy: file system → SVM → volume per PVC
- NetApp Trident via Helm; identity via EKS Pod Identity
- PVC Bound in about 8 s; df shows the claim size; online expand
- Delete claims and backends before uninstalling the operator

---

## Chapter 9 — Cleanup & Choosing Storage

**Starts at 11:17** · length 01:10 · source `S09-cleanup-and-choosing` · hook: *"Tear down in dependency order, then pick the right service"*

**What you'll learn.** This closing chapter has two parts: how to tear down everything the seven storage labs created without leaking AWS resources, and how to choose between the seven options. It follows `concepts/storage/08-cleanup-process.md` (dependency order, finalizers, reclaim policies, the Trident trap) and the comparison tables in `concepts/storage/09-diagrams.md` and the per-lab cheat-sheets. The cleanup was executed live on the `eks-workshop` cluster. The choosing matrix summarises the lab configurations, so its AZ column describes what the labs built, not every possible deployment.

### The golden rule: delete in dependency order

**[11:26]** Controllers and drivers must outlive the objects they clean up after.

> *On screen:* An eight-step dependency ladder is drawn top to bottom, from workloads and PVCs down to drivers, IAM and security groups.

The order that worked [LIVE] is: (1) workloads that use storage, (2) PVCs then PVs, (3) things Kubernetes created in AWS for you, (4) things you created by hand (file systems, mount targets, buckets), (5) the drivers and controllers, (6) their leftovers (CRDs, namespaces, StorageClasses), (7) IAM roles, policies and security groups, (8) local temp files and credentials. A PVC in use cannot be deleted, and a driver must still be running to delete the cloud volume behind a `Delete` PVC.

**[11:30]** IAM roles go near the end: drivers still need them during their own cleanup.

> *On screen:* The IAM role box slides to near the bottom of the ladder, with an arrow from the drivers still pointing at it.

Drivers call AWS with their IAM role during their own cleanup, for example deleting an EBS volume or an FSx child volume. Delete the role first and those calls fail, leaving objects stuck. Security groups also go late, because AWS refuses to delete a security group while any network interface (an FSx file system, a mount target, a load balancer) still uses it, and those interfaces only disappear once the resource is fully deleted [BG].

### Why: finalizers

**[11:36]** The controller deletes the AWS resource first, then removes the finalizer.

> *On screen:* An object marked with a deletionTimestamp waits while its controller deletes the AWS resource and then removes the finalizer tag.

A **finalizer** is a marker that says "don't really delete me until my controller has cleaned up". On `kubectl delete`, Kubernetes only sets `deletionTimestamp` and waits. The responsible controller deletes the external resource (volume, access point, load balancer), then removes its finalizer, and only then does the object disappear. That is how Kubernetes avoids orphaning cloud resources.

**[11:40]** Uninstall the controller first: the object hangs, and AWS keeps billing.

> *On screen:* The controller is removed first, the object hangs forever with its finalizer, and a billing meter keeps running on the AWS resource.

If you uninstall the controller before the objects it guards, nothing is left to remove the finalizer, and the object stays in `Terminating` indefinitely. That is exactly the Trident namespace trap from chapter 8 [LIVE]. Worse, any real AWS resource behind it is never deleted, so it keeps billing. Remove the objects, wait until they are gone, and uninstall the controller last.

### Deleting the PVC: who removes the storage?

**[11:48]** Delete: the driver removes only what it created. Retain or static: you remove it.

> *On screen:* A seven-row table fills in, with Delete rows in red and Retain rows in green, saying who removes the storage for each service.

With `reclaimPolicy: Delete`, the driver removes **only what it created**. [LIVE] EBS deleted the EBS volume, EFS deleted only the access point (the file system stayed), OpenZFS deleted the child volume, and Trident deleted the ONTAP volume (≈35 s). With `Retain` or static provisioning (Mountpoint S3, S3 Files, FSx Lustre), deleting the PVC leaves the PV `Released`, and you must delete the PV and the underlying bucket or file system yourself. A pre-existing file system is never deleted by a PVC.

### Choosing among the seven options

**[11:58]** Block for one pod; file systems for sharing; S3 when data lives in a bucket.

> *On screen:* A comparison matrix fills in row by row for all seven services: type, sharing, AZ scope and strength.

The matrix gives three families. **Block** (EBS) for one pod at a time (RWO) in a single AZ, typically StatefulSet databases. **Shared file systems** (EFS, S3 Files, FSx OpenZFS / Lustre / ONTAP) for many pods (RWX). **Object-backed** options (Mountpoint, S3 Files) when the data already lives, or must live, in a bucket. The AZ column reflects these labs: EFS and S3 Files are multi-AZ, the FSx file systems here were single-AZ (ONTAP can also be deployed multi-AZ).

**[12:03]** Fargate pods: EFS and S3 Files work; the three FSx services are EC2 only.

> *On screen:* The highlight moves to the EFS row, and Fargate badges appear next to EFS and S3 Files, with the three FSx rows marked EC2 only.

Fargate pods have no node you manage, so they can't load arbitrary kernel or CSI node plugins. In the source's comparison, EFS and S3 Files work from Fargate, while the three FSx services require EC2 nodes. If a workload must run on Fargate and needs shared files, EFS is the simple default; check the current AWS documentation before relying on any storage option with Fargate [BG].

**[12:07]** Lustre for raw parallel throughput; OpenZFS or ONTAP for low latency and data features.

> *On screen:* The highlight jumps to the Lustre row for throughput, then marks OpenZFS and ONTAP for low latency and data features.

Among the FSx options, **Lustre** wins on raw parallel throughput for ML and HPC, with a 1.2 TiB minimum and Lustre-client mounts. **OpenZFS** offers low-latency NFS with ZFS features (snapshots, compression), but [LIVE] claims took ≈76 s and sizes weren't enforced. **ONTAP** brings enterprise data management through Trident, with ≈8 s claims, exact sizes and online expansion. Choose by access pattern first (block vs shared vs bucket), then by performance and features.

### Key takeaways  `[12:13]`

- Delete workloads → claims → cloud objects → drivers → IAM
- Finalizers need their controller: never uninstall it first
- Delete policy removes only what the driver created
- Match the service to the access pattern, not the habit

# AWS EKS — Compute — Guide

Total length: **09:20**

**Video:** [`EKS-Compute.mp4`](EKS-Compute.mp4), 1920×1080, 30 fps, with chapter markers. In VLC use *Playback → Chapter*.
**Editable drawings:** [`EKS-Compute.excalidraw`](EKS-Compute.excalidraw). Open it at excalidraw.com with *Menu → Open*; each scene is a named frame.
**Source:** `EKS/AWS_EKS_fundamentals/`. Chapters follow the numbered files in `concepts/compute/` (01-mng-basics … 06-fargate) and `labs/09–14`, in order.

**Execution status:** **All 6 compute labs were executed live** (managed node groups, Cluster Autoscaler with over-provisioning, Graviton, Spot, Karpenter, Fargate). Timings are measured.

### How to use this guide
- Each **[mm:ss]** line is the on-screen caption, with its exact time in this video.
- *On screen* describes the animation; the paragraph under it explains the idea and the kubectl/YAML/AWS pieces involved.
- Tags follow the source notes: **[LIVE]** = measured on a real EKS cluster, **[W]** = stated by the EKS Workshop, **[BG]** = background knowledge (verify before relying on it). Account IDs and IPs are never shown.

## Chapters

| Starts | Chapter | Length | Source video |
|---|---|---|---|
| 00:00 | [Introduction](#introduction) | 00:12 | `00-intro` |
| 00:12 | [Chapter 1 — Managed Node Groups](#chapter-1--managed-node-groups) | 01:35 | `C01-managed-node-groups` |
| 01:48 | [Chapter 2 — Cluster Autoscaler](#chapter-2--cluster-autoscaler) | 01:31 | `C02-cluster-autoscaler` |
| 03:20 | [Chapter 3 — Graviton (ARM) node groups](#chapter-3--graviton-arm-node-groups) | 01:29 | `C03-graviton` |
| 04:49 | [Chapter 4 — Spot instances on EKS](#chapter-4--spot-instances-on-eks) | 01:36 | `C04-spot` |
| 06:26 | [Chapter 5 — Karpenter: group-less autoscaling](#chapter-5--karpenter-group-less-autoscaling) | 01:32 | `C05-karpenter` |
| 07:58 | [Chapter 6 — Fargate: serverless pods](#chapter-6--fargate-serverless-pods) | 01:22 | `C06-fargate` |

---

## Introduction

**Starts at 00:00** · length 00:12 · source `00-intro` · hook: *"Where your pods run, and how nodes appear and disappear"*

**What you'll learn.** This intro lists the six compute chapters in the order of `concepts/compute/` (01-mng-basics … 06-fargate), which matches `labs/09`–`labs/14`. Every one of these labs was executed live on the workshop cluster (Kubernetes 1.33, 3 × m5.large), so the timings in this video are measured, not quoted.

### What this video covers

**[00:07]** All six labs were executed live; timings are measured.

> *On screen:* The six chapter titles type in one by one next to numbered circles, then the caption about live timings appears.

Each chapter answers one question about where pods run: on nodes you size yourself (managed node groups, Graviton, Spot), on nodes added for you (Cluster Autoscaler, Karpenter), or with no nodes to manage at all (Fargate). The chapters are ordered as in the source so later ones can build on earlier ones; Karpenter, for example, is easier to follow once you have seen Cluster Autoscaler grow a node group. Tags in the guide follow the source notes: [LIVE] measured, [W] workshop text, [BG] background.


---

## Chapter 1 — Managed Node Groups

**Starts at 00:12** · length 01:35 · source `C01-managed-node-groups` · hook: *"What really happens when you ask EKS for one more node?"*

**What you'll learn.** This chapter follows `concepts/compute/01-mng-basics/` (01-add-nodes, 02-pod-affinity-and-anti-affinity, 03-upgrading-amis) and `labs/09-compute-mng-basics.md`. It shows what a managed node group really is (an Auto Scaling group that EKS operates), the measured timeline of adding a node, how hard affinity rules can leave pods Pending even when capacity is free, and how an AMI upgrade replaces nodes without dropping capacity. All three parts were run live.

### A managed node group = an Auto Scaling group EKS looks after

**[00:17]** Workshop start: 3 × m5.large, one per AZ. EKS joins, labels and drains them; you pay only for EC2.

> *On screen:* A node-group box opens with three m5.large nodes, one in each Availability Zone, under an 'Auto Scaling group managed by EKS' label.

A managed node group is an EC2 Auto Scaling group that EKS creates and operates for you: it picks the EKS-optimised AMI, joins nodes to the cluster, adds labels such as `eks.amazonaws.com/nodegroup`, and drains nodes before replacing them. You still pay normal EC2 prices; there is no extra charge for the management. The workshop starts with three m5.large nodes spread across three AZs, which is the baseline every later chapter changes.

### Add a node: the real timeline [LIVE]

**[00:24]** Desired 3 → 4. The request is accepted and the ASG's desired capacity changes.

> *On screen:* The desired-count chip flips from 3 to 4 and a fourth, empty node slot appears.

Scaling a node group is a request to EKS, for example `aws eks update-nodegroup-config --scaling-config desiredSize=4` or `eksctl scale nodegroup`. EKS only changes the desired capacity on the underlying ASG; the ASG then does the actual work. Nothing in Kubernetes changes yet at this point.

**[00:27]** 11 s later the Auto Scaling group launches the EC2 instance.

> *On screen:* A marker moves along the timeline to +11 s and the new node outline is drawn as an EC2 instance launches.

[LIVE] The ASG launched the EC2 instance 11 s after the request. This is plain EC2 behaviour: the instance boots from the node group's launch template and runs the bootstrap that will later register it with the cluster.

**[00:29]** At +19 s EKS reports the update 'Successful'. That only means the settings were applied.

> *On screen:* The marker reaches +19 s with an 'update Successful' badge, while the node is still not part of the cluster; a 'Successful ≠ Ready' warning pops up.

[LIVE] EKS marked the update 'Successful' at about +19 s (derived from the log timestamps). That status means the node group settings were applied, not that a usable node exists. If a script waits only for this status, it will move on before the node can run pods, which is a common automation bug.

**[00:34]** 37 s after launch the kubelet registers the node. It is NotReady: the CNI is still starting.

> *On screen:* At +37 s the node turns grey with a NotReady label as the kubelet registers.

[LIVE] 37 s after launch the kubelet registered the Node object, but it was NotReady because the VPC CNI (aws-node) was still starting on it. A node is not Ready until its network plugin is up, because pods scheduled there could not get an IP address.

**[00:38]** 17 s later it is Ready. About 65 s from your command to a usable node.

> *On screen:* After another 17 s the node turns green with Ready, and the total of about 65 s is shown.

[LIVE] The node became Ready 17 s later, so about 65 s passed from the command to a node that can accept pods. Remember this number: it is the boot delay that over-provisioning (Chapter 2) and Karpenter (Chapter 5) try to shorten or hide. To check readiness, use `kubectl get nodes` or `kubectl wait --for=condition=Ready node/...`.

### Pod affinity and anti-affinity: together, or apart

**[00:46]** One checkout replica lands on node A: the only node that already runs redis.

> *On screen:* A redis pod sits on node A; the first checkout replica slides onto the same node.

Pod affinity says 'schedule me near pods with this label'. Here checkout has a hard (`requiredDuringSchedulingIgnoredDuringExecution`) affinity to redis with `topologyKey: kubernetes.io/hostname`, so it may only land on a node that already runs redis. Only node A does, so that is where the first replica goes.

**[00:51]** Scale checkout to 2: the second replica is Pending. Node A already has a checkout.

> *On screen:* Checkout is scaled to 2 and the second replica appears in a Pending box with no node to go to.

Checkout also has a hard anti-affinity to itself on `kubernetes.io/hostname`: no two checkout replicas on the same node. Combined with the redis affinity, the second replica needs a node with redis but without checkout, and none exists, so it stays Pending. Hard rules are never relaxed to make room.

**[00:56]** Spread redis with anti-affinity: redis #2 goes to node B, and checkout #2 follows at once.

> *On screen:* A second redis replica moves to node B because of anti-affinity, and the Pending checkout immediately follows it there.

Giving redis its own anti-affinity spreads its two replicas over two nodes. As soon as redis #2 is on node B, node B satisfies both checkout rules (redis present, no checkout yet), and the Pending checkout is scheduled there immediately. The scheduler reacts to changes in the cluster; you did not touch checkout at all.

**[01:02]** Replica 3 stays Pending: 2 nodes have no redis, 2 already run a checkout.

> *On screen:* A third checkout replica appears and stays Pending; the scheduler's message lists why every node was rejected.

A third checkout replica needs a third node that runs redis and no checkout. Two nodes have no redis and two already run a checkout, so the scheduler reports something like '0/4 nodes are available' with the failed rules. Reading this message is the fastest way to debug Pending pods: `kubectl describe pod <name>` shows it under Events.

**[01:06]** Node D sat idle: spare capacity can't help when a hard rule excludes the node.

> *On screen:* Node D is highlighted as idle while the Pending pod still cannot use it.

Node D had free CPU and memory the whole time, but hard affinity excluded it, so free capacity did not help. This is the trade-off of `required...` rules: they are guarantees, not preferences. If being near redis is only nice to have, `preferredDuringSchedulingIgnoredDuringExecution` lets the scheduler fall back to node D.

### Upgrading the AMI: surge, cordon, drain, replace

**[01:12]** update-nodegroup-version: EKS moves every node to the latest EKS-optimised AMI.

> *On screen:* The update-nodegroup-version command card appears above the node group.

`aws eks update-nodegroup-version` (or `eksctl upgrade nodegroup`) moves the group to the latest EKS-optimised AMI for its Kubernetes version. EKS performs the rollout for you; you do not replace instances yourself. This is how OS and kubelet patches reach managed nodes.

**[01:16]** Surge first: new nodes join before old ones leave. EKS raised the ASG max from 6 to 10.

> *On screen:* Four new nodes surge in beside the old ones and the ASG max chip changes from 6 to 10.

[LIVE] EKS surges first: it raises the ASG's max (6 → 10 here) and launches new nodes before removing old ones, so capacity never drops. The setting was `maxUnavailablePercentage: 50`, which allowed 2 of the 4 nodes to be replaced in parallel. Surging needs spare EC2 quota and subnet IPs, which is the cost of a safe upgrade.

**[01:22]** Each old node is cordoned, then drained, respecting PodDisruptionBudgets.

> *On screen:* Old nodes get a cordon barrier, then their pods drain off onto the new nodes.

Each old node is cordoned (marked unschedulable) and then drained: pods are evicted through the Eviction API, so PodDisruptionBudgets are respected. In the workshop the retail-store pods had no PDBs and a single replica, so a drain briefly removed each such service; in production, run at least 2 replicas with a PDB so a drain never takes a service fully down.

**[01:28]** Old instances terminated, max restored: about 12 minutes for 4 nodes, never below capacity.

> *On screen:* The old nodes are crossed out and removed, the max returns to 6, and a timer shows about 12 minutes.

[LIVE] When the old instances were terminated, EKS set the ASG max back to 6. The whole upgrade of 4 nodes took about 12 minutes, which is normal for a rolling replacement. Plan upgrades in maintenance windows and watch `kubectl get nodes -o wide` to see AMI versions change.

### Key takeaways  `[01:33]`

- A managed node group is an ASG of EC2 nodes that EKS manages
- 'Update Successful' is not 'node Ready': about 65 s to a usable node
- AMI update: surge, cordon, drain, replace (≈12 min for 4 nodes)

---

## Chapter 2 — Cluster Autoscaler

**Starts at 01:48** · length 01:31 · source `C02-cluster-autoscaler` · hook: *"Pods are Pending. Who adds the node?"*

**What you'll learn.** This chapter follows `concepts/compute/02-cluster-autoscaler/` and `labs/10-compute-cluster-autoscaler.md`, including the over-provisioning pages. It explains the Pending-pod → Cluster Autoscaler → ASG loop, then walks through a live scale-out, the deliberately slow scale-in, and how low-priority pause pods hide node boot time. All numbers are [LIVE]; builds on Chapter 1's node groups.

### Pending pods → Cluster Autoscaler → ASG desired +N

**[01:53]** CA watches for Pending pods that cannot fit, then raises the ASG's desired size.

> *On screen:* Pending pods appear, an arrow runs to a Cluster Autoscaler box, and another arrow raises the ASG's desired count.

Cluster Autoscaler (CA) is a Deployment in the cluster. It looks for pods that are Pending because no node has room, simulates whether adding a node from one of the node groups would let them schedule, and if so raises that ASG's desired capacity. It does not react to CPU usage; it reacts to unschedulable pods, which is why requests matter.

**[01:59]** It finds node groups by ASG tags, and its IAM role may only write to those tagged ASGs.

> *On screen:* Tag chips appear on the ASG and an IAM policy card shows that writes are limited to ASGs carrying those tags.

CA discovers node groups by ASG tags, `k8s.io/cluster-autoscaler/enabled` and `k8s.io/cluster-autoscaler/<cluster-name>`, which managed node groups get automatically. Its IAM role (via IRSA in the workshop) should be scoped with a condition on those tags, so CA can change only the ASGs it is meant to manage. A missing tag is the most common reason CA ignores a group.

### Scale-out: the real run (8 replicas per app) [LIVE]

**[02:05]** Three of four nodes sit at 90 % CPU requests. Scale every app to 8: 16 pods Pending.

> *On screen:* Three node bars fill to 90% CPU requests and 16 pods drop into a Pending area.

[LIVE] Before the test, three of the four nodes were at about 90% of their CPU requests. Scaling each app to 8 replicas created 16 pods that could not fit anywhere and went Pending. That Pending state is exactly the signal CA watches.

**[02:11]** Within 10 s CA logs 'Estimated 2 nodes needed' and sets the group from 4 to 6.

> *On screen:* A log line 'Estimated 2 nodes needed' types out at +10 s and the desired count changes from 4 to 6.

[LIVE] Within 10 s CA logged 'Estimated 2 nodes needed' and set the node group's desired size from 4 to 6. CA computes how many nodes of the group's instance type would fit the pending pods, then asks for that many in one step, capped by the group's max.

**[02:17]** Both nodes are Ready 35 s after the decision, and the scheduler fills them.

> *On screen:* Two new nodes join, turn Ready at the 35 s mark, and Pending pods move onto them.

[LIVE] Both new nodes were Ready about 35 s after CA's decision, and the scheduler immediately placed pending pods on them. The total time a user waits is CA decision + EC2 boot + node join, which is why over-provisioning (later in this chapter) exists.

**[02:21]** 4 pods stay Pending for good: the node group hit its max size of 6. Max is a cost guard.

> *On screen:* Four pods remain in the Pending area under a 'max size 6' cap.

[LIVE] Four pods stayed Pending permanently because the node group reached its max size of 6. Max size is a cost guard: CA never goes past it, no matter how many pods are pending. If you see Pending pods with CA logs mentioning max size, raise the max or reduce requests.

### Scale-in is slow on purpose

**[02:28]** Apps back to 1 replica: nodes whose pods request under 50 % become 'unneeded'.

> *On screen:* Apps scale back to 1 replica and several nodes turn amber with an 'unneeded' label.

[LIVE] After scaling the apps back to 1 replica, CA marks a node as 'unneeded' when the requests of its pods are below the utilisation threshold (50% by default) and those pods can be moved elsewhere. Being unneeded does not trigger removal immediately.

**[02:33]** CA waits: a node must stay unneeded for 10 minutes before it is removed.

> *On screen:* A timer counts up to 10 minutes beside the unneeded nodes.

CA waits until a node has been unneeded for `scale-down-unneeded-time`, 10 minutes by default, before removing it. This delay is on purpose: it avoids removing a node right before load comes back, which would cause churn and new boot delays. [LIVE] Scale-in happened about 10 minutes after the scale-down.

**[02:39]** Then it drains and terminates those exact instances, stopping at min size 3.

> *On screen:* The unneeded nodes are drained and removed until the group reaches its minimum of 3.

CA then drains the chosen nodes (respecting PodDisruptionBudgets) and terminates those exact instances, reducing desired capacity accordingly. It never goes below the group's min size, which was 3 here. Pods with local storage or without a controller can block scale-down unless configured otherwise [BG].

### Over-provisioning: hide the node boot time

**[02:45]** Pause pods at priority −1 each hold a whole spare node; real pods get the default 0.

> *On screen:* Two pause pods with priority -1 each occupy a whole spare node; app pods are labelled priority 0.

Over-provisioning runs 'pause' pods that do nothing but reserve resources. They use a PriorityClass with value -1 (`priorityClassName: pause-pods`), while normal pods have the default priority 0. In the lab each pause pod requested about 6.5 Gi, so each one held a whole spare node; setting this up grew the group from 3 to 5 nodes in 52 s [LIVE].

**[02:51]** Scale every app to 7 replicas. 9 s later the scheduler preempts both pause pods.

> *On screen:* Apps scale to 7 replicas and, at +9 s, both pause pods are knocked off their nodes.

[LIVE] When the apps were scaled to 7 replicas, the scheduler needed room and preempted (evicted) the lower-priority pause pods 9 s later. Preemption is a scheduler feature: a pending pod with higher priority can displace lower-priority pods.

**[02:56]** App pods start at once on the spare nodes: 15 of 20 ran within 29 s.

> *On screen:* App pods move onto the freed spare nodes and a counter shows 15 of 20 running within 29 s.

[LIVE] The app pods started at once on the nodes the pause pods had been holding: 15 of 20 were running within 29 s, compared with about 65–75 s with plain Cluster Autoscaler. The boot time still happens, but the buffer absorbs it so users don't wait.

**[03:01]** The evicted pause pods go Pending, so CA adds a node to refill the buffer, up to max 6.

> *On screen:* The evicted pause pods go Pending and Cluster Autoscaler adds another node to rebuild the buffer.

The evicted pause pods are now Pending themselves, which triggers CA to add a node and rebuild the buffer, up to the group's max of 6. The cost of over-provisioning is paying for idle spare capacity; size the pause pods to the burst you expect.

### Key takeaways  `[03:08]`

- CA turns Pending pods into a bigger ASG desired size
- Scale-out in seconds; scale-in after 10 min unneeded
- Pause pods (priority −1) hide boot time, at a standing cost

---

## Chapter 3 — Graviton (ARM) node groups

**Starts at 03:20** · length 01:29 · source `C03-graviton` · hook: *"Same cluster, a different CPU architecture"*

**What you'll learn.** This chapter follows `concepts/compute/03-graviton/` and `labs/11-compute-graviton.md`: creating an ARM (Graviton) managed node group, tainting it, and steering a workload onto it with a nodeSelector plus a toleration. It finishes with a live comparison of the NoSchedule and NoExecute taint effects. Executed live; the price/performance claims are workshop figures only.

### Graviton = ARM CPUs on EC2

**[03:25]** Graviton instances use ARM CPUs. The 'g' in the family name gives them away: t4g, m7g.

> *On screen:* An ARM chip icon appears with Graviton family names such as t4g and m7g, the 'g' highlighted.

Graviton is AWS's own ARM-based CPU line. Instance families with a 'g' after the generation number (t4g, m7g, c7g) use Graviton; Kubernetes reports these nodes with the label `kubernetes.io/arch=arm64`. From the cluster's point of view they are ordinary nodes; the difference is the CPU instruction set.

**[03:30]** These are workshop figures vs comparable 5th-gen x86, not measured here.

> *On screen:* Price and performance bars appear with a 'workshop figures, not measured' label.

[W] The workshop states that Graviton offers better price/performance and lower energy use than comparable 5th-generation x86 instances. These figures were not measured in this project, so treat them as vendor claims and benchmark your own workload before switching.

**[03:34]** Containers must be built for arm64. The retail-store images are multi-arch, so both work.

> *On screen:* An image card shows both amd64 and arm64 variants inside one multi-arch tag.

An ARM node can only run container images built for arm64. Multi-architecture images publish one tag that points to an image index containing both amd64 and arm64 builds, and the container runtime pulls the matching one. The retail-store images are multi-arch, which is why the same Deployment can run on both node types; a single-arch amd64 image would fail with an 'exec format error'.

### Create a separate ARM node group

**[03:41]** A new managed node group: t4g.medium with the arm64 build of Amazon Linux 2023.

> *On screen:* A new node-group box for t4g.medium with the arm64 Amazon Linux 2023 AMI is drawn next to the x86 group.

The lab creates a separate managed node group with an ARM instance type (t4g.medium) and the arm64 build of Amazon Linux 2023 (ami type `AL2023_ARM_64_STANDARD` [BG]). Keeping x86 and ARM in different node groups lets you scale and taint them independently.

**[03:46]** Live: the ARM node was Ready in about 1 min 15 s, the group ACTIVE in about 1 min 50 s.

> *On screen:* Timers show the ARM node Ready at about 1 min 15 s and the group ACTIVE at about 1 min 50 s.

[LIVE] The ARM node was Ready about 1 min 15 s after creation started, and the node group reached ACTIVE at about 1 min 50 s. As in Chapter 1, ACTIVE and Ready are different signals; wait for the node to be Ready before scheduling onto it.

### Taint the node group, not the node

**[03:53]** A group-level taint is applied to every node in the group, today's and future ones.

> *On screen:* A taint barrier labelled frontend=true:NoExecute is drawn across the whole ARM node group.

The lab puts a taint on the node group itself (`--taints` with key frontend, value true, effect NoExecute). EKS applies a node-group taint to every node in the group, including nodes created later by scaling or replacement. A taint repels pods: only pods with a matching toleration may run there.

**[03:58]** Tainting a node by hand is lost when it's replaced. Here the taint took about 70 s to appear.

> *On screen:* A hand-applied taint on a single node fades away as the node is replaced, and a 70 s timer shows the group taint appearing.

A taint added with `kubectl taint node ...` lives only on that Node object and is lost when the instance is replaced, for example during an AMI upgrade or a scale-in/scale-out. [LIVE] After setting the group-level taint, it took about 70 s to appear on the node, so check with `kubectl describe node` before testing.

### Step 1: nodeSelector only → Pending

**[04:05]** Step 1: give ui a nodeSelector kubernetes.io/arch=arm64 only. The new pod is Pending.

> *On screen:* The ui Deployment gets a nodeSelector chip kubernetes.io/arch=arm64 and its new pod sits in Pending.

Step 1 adds only `nodeSelector: kubernetes.io/arch: arm64` to the ui Deployment. A nodeSelector attracts a pod to nodes with that label, but it cannot override a taint. The rollout creates a new pod, which stays Pending.

**[04:08]** The x86 nodes fail the selector; the one ARM node fails the taint. The old pod keeps serving.

> *On screen:* Arrows from the pod bounce off the x86 nodes (selector fails) and off the ARM node (taint), while the old ui pod keeps running.

The scheduler's message explains it: the x86 nodes fail the nodeSelector, and the single ARM node has the frontend taint the pod does not tolerate, so 0 nodes qualify. Because the rollout keeps the old ReplicaSet until the new pod is Ready, the old ui pod keeps serving traffic; nothing breaks while you fix the spec.

### Step 2: add the toleration → Running

**[04:15]** Step 2: add a toleration for the frontend taint, like a wristband for the bouncer.

> *On screen:* A toleration 'wristband' is attached to the ui pod template.

Step 2 adds a toleration for `frontend=true:NoExecute`. A toleration is like a wristband: it lets the pod past the bouncer (the taint), but it does not send the pod there. That is why you need both pieces: the nodeSelector to attract the pod to ARM, the toleration to be allowed in.

**[04:19]** It now runs on the Graviton node: uname -m prints aarch64.

> *On screen:* The new ui pod passes the barrier onto the ARM node and a terminal prints aarch64.

With both the selector and the toleration, the new ui pod is scheduled on the Graviton node and the rollout completes. [LIVE] Running `uname -m` inside the container printed `aarch64`, confirming the ARM build of the image is running.

### NoSchedule vs NoExecute, tested live

**[04:26]** Add demo=one:NoSchedule: the running probe stays, but a new probe2 is Pending.

> *On screen:* A NoSchedule taint is added: the running probe pod stays, while a new probe2 pod waits in Pending.

[LIVE] NoSchedule only affects new scheduling decisions: after adding `demo=one:NoSchedule` to the node, the already-running probe pod kept running, but a new pod without a toleration (probe2) went Pending. Use NoSchedule when you want to stop new work without disturbing what is there.

**[04:31]** Add demo=two:NoExecute instead: the running probe is evicted within seconds.

> *On screen:* A NoExecute taint is added instead and the running probe pod is evicted from the node.

[LIVE] NoExecute also evicts running pods that do not tolerate the taint: after adding `demo=two:NoExecute`, the running probe pod was evicted within seconds. A toleration can include `tolerationSeconds` to delay that eviction [BG]. This is why the lab's frontend taint is NoExecute: it keeps the ARM group exclusive for the ui.

### Key takeaways  `[04:36]`

- Graviton = ARM EC2; images must be arm64 or multi-arch
- Taint the node group: it reached the node in about 70 s
- A pod needs a toleration (allowed) and a nodeSelector (sent there)

---

## Chapter 4 — Spot instances on EKS

**Starts at 04:49** · length 01:36 · source `C04-spot` · hook: *"Spare EC2 capacity at a big discount — that AWS can take back"*

**What you'll learn.** This chapter follows `concepts/compute/04-spot/` (instance-type diversification, creating Spot capacity, running a workload on Spot, cheatsheet) and `labs/12-compute-spot.md`. It explains Spot pools and diversification, creates a Spot managed node group, pins a stateless service to it, and shows a live node-loss timeline, plus an honest lesson about an invalid test result. Executed live.

### Spot = spare EC2 capacity, 2-minute notice

**[04:55]** Same machine, about 66% cheaper here. The catch: AWS can reclaim it with 2 minutes' notice.

> *On screen:* Two price bars compare On-Demand and Spot for the same instance, with a '2-minute notice' warning.

Spot instances are spare EC2 capacity sold at a discount. [LIVE] The c5.large Spot price observed was about $0.029/h against the workshop's On-Demand figure of $0.085/h, roughly 66% cheaper (the comparison mixes a live Spot price with a workshop On-Demand number, as the source does). The catch: AWS can reclaim the instance with a 2-minute interruption notice, so only interruption-tolerant workloads belong on Spot.

### Spot pools: one instance type in one AZ

**[05:00]** A pool = one type, OS and AZ, priced on its own: c5.large is $0.0286 to $0.0313.

> *On screen:* A grid of instance types by Availability Zone appears, each cell showing its own Spot price.

A Spot capacity pool is one instance type, OS and Availability Zone; each pool has its own price and its own supply. [LIVE] c5.large alone ranged from $0.0286 to $0.0313 across AZs. Pools are reclaimed independently, which is the basis for diversification.

**[05:05]** If one pool runs dry, the other 13 can still supply capacity. That is diversification.

> *On screen:* One pool in the grid is crossed out while the remaining pools stay available.

If you ask for many instance types across several AZs, one pool running out of capacity does not stop you, because the other pools can still supply instances. In the lab's grid, losing one pool still left 13 others. This is the single most effective way to make Spot reliable.

**[05:10]** Pick same-size types: 2 vCPU and 4 GiB. Cluster Autoscaler sizes a group from its first type.

> *On screen:* A list of same-size instance types (2 vCPU, 4 GiB) is highlighted, with a note about Cluster Autoscaler sizing.

Choose instance types of the same size (here 2 vCPU and 4 GiB, e.g. c5.large, c5a.large, m5.large-class equivalents) in one node group. Cluster Autoscaler assumes every node in a group looks like the group's first instance type when it simulates scale-out, so mixing sizes makes its estimates wrong [W]. A query in the lab returned 17 matching types [LIVE].

### Create Spot capacity: a managed node group

**[05:17]** One flag, --capacity-type SPOT, makes every node in the group Spot.

> *On screen:* The create-nodegroup command appears with the --capacity-type SPOT flag highlighted.

Creating Spot capacity is one flag on a managed node group: `aws eks create-nodegroup ... --capacity-type SPOT --instance-types <list>` (or the eksctl equivalent). Every node in that group is Spot, and EKS labels each node `eks.amazonaws.com/capacityType=SPOT`, which workloads can select on.

**[05:19]** Behind it: an Auto Scaling group using price-capacity-optimized, with capacity rebalance on.

> *On screen:* The Auto Scaling group behind it is shown with price-capacity-optimized and capacity rebalance settings.

EKS builds the ASG with the allocation strategy price-capacity-optimized, which picks pools that are both cheap and deep (less likely to be interrupted), and enables Capacity Rebalancing so the ASG can start a replacement when AWS signals elevated interruption risk [BG for the strategy meaning]. On-Demand base capacity is 0%, so the group is fully Spot.

**[05:24]** Live: ready in about 1 min 50 s, two c5.large nodes in two different AZs.

> *On screen:* Two c5.large Spot nodes appear in two different AZs with a ready timer of about 1 min 50 s.

[LIVE] The Spot node group was ACTIVE in about 1 min 50 s with two c5.large nodes in two different AZs. Spreading across AZs is part of diversification: an interruption wave in one AZ affects only part of your capacity.

### Pin the stateless service to Spot

**[05:31]** A nodeSelector on the Spot label moves catalog onto a Spot node.

> *On screen:* A nodeSelector chip moves the catalog pod onto a Spot node.

The lab adds `nodeSelector: eks.amazonaws.com/capacityType: SPOT` to the catalog Deployment, so its pods are rescheduled onto Spot nodes. Catalog is stateless: any replica can serve any request, and a lost pod is simply recreated elsewhere.

**[05:34]** The MySQL database is not pinned: state does not belong on capacity that can vanish.

> *On screen:* The MySQL pod stays on an On-Demand node, marked 'state stays off Spot'.

The catalog MySQL database is deliberately not pinned to Spot. A stateful pod on reclaimed capacity loses its node, and with EBS-backed storage it can only restart in the same AZ (see the Storage video), so recovery is slow and risky. Keep databases and other state on On-Demand capacity.

### Reality check: terminate a Spot node (live)

**[05:43]** Two replicas on two Spot nodes. Then the instance under one of them was terminated.

> *On screen:* Two catalog replicas run on two Spot nodes; the EC2 instance under one of them is marked for termination.

[LIVE] To see what an interruption looks like, the instance under one of two catalog replicas was terminated directly. Note that this is harsher than a real Spot interruption, which comes with a 2-minute warning that lets the node be drained first.

**[05:45]** At 12:22:59 node A's EC2 instance shut down.

> *On screen:* The timeline starts at 12:22:59 and node A goes dark.

[LIVE] Node A's EC2 instance shut down at 12:22:59. From this moment the pods on it stopped serving, but Kubernetes did not know yet.

**[05:47]** 43 s later Kubernetes marked it NotReady: it waits for missed kubelet heartbeats.

> *On screen:* At +43 s node A is labelled NotReady.

[LIVE] 43 s later the node controller marked the node NotReady. Kubernetes detects a lost node by missed kubelet heartbeats (node leases), so there is always a detection delay. During this window the Service could still send traffic to the dead pod's endpoint.

**[05:50]** At +97 s the ASG noticed and launched a replacement: it heals toward desired = 2.

> *On screen:* At +97 s the ASG launches a replacement node.

[LIVE] At +97 s the ASG noticed the terminated instance and launched a replacement, healing back to desired = 2. The ASG works independently of Kubernetes: it only cares that the instance count matches desired capacity.

**[05:53]** New node Ready ~2 min after the loss; 2 endpoints at +175 s. (Real Spot sends a 2-min warning first.)

> *On screen:* The replacement turns Ready about 2 minutes after the loss, and at +175 s two endpoints are shown.

[LIVE] The new node was Ready about 2 minutes after the loss, and the Service had 2 endpoints again at +175 s. With a real Spot interruption, the 2-minute notice (handled by the node group or an interruption handler) lets EKS cordon and drain the node before it disappears, which shortens or removes this gap.

### Lesson: the '0 failed probes' result was invalid

**[06:01]** The probe measuring downtime ran on the node that was killed, so it died too.

> *On screen:* The probe pod is drawn on the killed node and is crossed out together with it.

[LIVE] The test recorded '0 failed probes', but the probe pod that measured availability was running on the node that was killed, so it died with it and measured nothing. The source keeps this mistake on purpose: the result is invalid and must not be quoted as evidence of zero downtime.

**[06:05]** A valid test puts the probe on a different, On-Demand node. It was not re-run.

> *On screen:* A corrected setup shows the probe on a separate On-Demand node, labelled 'not re-run'.

A valid version of the test runs the probe on a different node that is not Spot, for example an On-Demand node pinned with a nodeSelector, so the measurement survives the failure. This was not re-run, so the source has no valid downtime number for Spot node loss.

### Key takeaways  `[06:14]`

- Spot: about 66% cheaper here, reclaimable with 2 min notice
- Diversify across many same-size types and AZs (pools)
- Live loss: NotReady +43 s, replacement Ready ~2 min

---

## Chapter 5 — Karpenter: group-less autoscaling

**Starts at 06:26** · length 01:32 · source `C05-karpenter` · hook: *"Pods are Pending. Which machine fits them best and cheapest?"*

**What you'll learn.** This chapter follows `concepts/compute/05-karpenter/` (install, NodePool and EC2NodeClass, automatic node provisioning, disruption/consolidation, cleanup) and `labs/13-compute-karpenter.md`. It contrasts Karpenter with Cluster Autoscaler, then shows live provisioning (5 pods Running in 34 s on one m5.large) and live consolidation removing an empty node. Executed live with Karpenter 1.9.0.

### Node groups vs a travel agent for pods

**[06:30]** CA grows a node group. Karpenter reads pending pods and books one EC2 instance that fits.

> *On screen:* A node-group box (Cluster Autoscaler) and a 'travel agent' Karpenter box are compared side by side, the latter booking a single fitting instance.

Cluster Autoscaler can only grow existing node groups, each with fixed instance types. Karpenter has no node groups: it reads the requirements of the pending pods (CPU, memory, architecture, zone, capacity type) and launches an EC2 instance that fits them directly through the EC2 API, like a travel agent booking the right flight for each group. This usually gives faster scale-out and better bin-packing.

**[06:35]** Later it removes nodes that are empty, expired, drifted or wasteful: disruption.

> *On screen:* Disruption reasons appear as chips: empty, expired, drifted and underutilised.

Karpenter also manages the end of a node's life, which it calls disruption: it removes nodes that are empty, have reached their expiry (`expireAfter`, 72h in the lab), have drifted from their NodePool/EC2NodeClass spec, or can be replaced by something cheaper (consolidation). Pods with `karpenter.sh/do-not-disrupt` are protected [BG].

### Install (live: Karpenter 1.9.0)

**[06:41]** Prerequisites first: two IAM roles, an interruption queue, and tags so it can find subnets.

> *On screen:* Prerequisite cards appear: two IAM roles, an SQS interruption queue and subnet/security-group discovery tags.

[LIVE] Before installing Karpenter 1.9.0 with Helm, the lab created: a controller IAM role (IRSA), a node IAM role for the instances it launches, an SQS interruption queue (so Karpenter can react to Spot interruptions and rebalance events), and `karpenter.sh/discovery` tags on subnets and security groups. The Karpenter Deployment itself runs on the existing managed node group [BG]; it was ready in about 8 s.

**[06:46]** Cluster Autoscaler was removed first, so two autoscalers would not fight.

> *On screen:* The Cluster Autoscaler box is crossed out before Karpenter starts.

Cluster Autoscaler was removed first. Two autoscalers watching the same pending pods would both try to add capacity and could fight over scale-down decisions, so the source runs only one at a time.

### NodePool + EC2NodeClass

**[06:51]** NodePool says WHAT is allowed. EC2NodeClass says HOW to build it on AWS.

> *On screen:* A NodePool card (what is allowed) and an EC2NodeClass card (how to build it) appear and link together.

A NodePool (`karpenter.sh/v1`) describes what Karpenter may create: allowed instance categories/types, capacity type (on-demand here), architecture, limits and the disruption policy (`consolidationPolicy: WhenEmptyOrUnderutilized`, `consolidateAfter: 1m`). An EC2NodeClass describes how to build it on AWS: AMI family, node IAM role, and subnet/security-group selectors using the discovery tags.

**[06:55]** Live: both Ready ~16 s after apply. No discovery tags = no subnets = never Ready.

> *On screen:* Both cards switch to Ready at about 16 s; a warning shows that missing discovery tags means never Ready.

[LIVE] Both objects reported Ready about 16 s after `kubectl apply`. If the discovery tags are missing, the EC2NodeClass cannot resolve any subnets or security groups and never becomes Ready, and Karpenter will not launch nodes; check `kubectl describe ec2nodeclass` when nothing happens.

### Automatic provisioning (live)

**[07:02]** Scale to 5 pods, 5 GiB requested. Nothing fits, so they sit Pending.

> *On screen:* Five 1 GiB pods appear in a Pending row.

[LIVE] The lab's inflate Deployment was scaled to 5 replicas, each requesting 1 GiB, with a nodeSelector for the Karpenter node type, so no existing node could take them and all 5 went Pending. Karpenter batches pending pods for a moment so it can size one node for the whole group.

**[07:04]** Karpenter checks the allowed shapes: c5.large is too small for 5 GiB plus overhead.

> *On screen:* Instance shapes are listed and c5.large is rejected as too small.

Karpenter filters the instance types allowed by the NodePool against the batch's needs. c5.large has 4 GiB of memory, and after system reservations (kubelet, OS, DaemonSets) it cannot hold 5 GiB of requests, so it is rejected. This is why Karpenter compares allocatable resources, not the instance's headline size.

**[07:10]** Among those that fit, it takes the cheapest: one m5.large, on-demand.

> *On screen:* m5.large is highlighted as the cheapest shape that fits and a node box appears.

Among the shapes that fit, Karpenter picks the cheapest for on-demand: one m5.large (8 GiB). One node for all five pods is better bin-packing than Cluster Autoscaler would get from a fixed-type group.

**[07:13]** 34 s from the scale command to 5 Running pods, all bin-packed on one node.

> *On screen:* A timeline ticks +3, +6, +22 and +34 s and all five pods turn Running on the one node.

[LIVE] From the scale command at 12:38:34: at about +3 s Karpenter logged 'found provisionable pod(s)' and computed a single NodeClaim for all 5 pods; at about +6 s it launched the m5.large on-demand instance; at +22 s the kubelet registered the node; and at +34 s the NodeClaim was initialized and all 5 pods were Running. The +3 s and +6 s offsets are rounded from the log timestamps. Compare this with about 65 s for a managed node group node in Chapter 1.

### Disruption: consolidation (live)

**[07:19]** Scale to 12 pods: a second m5.large joins, 6 pods on each node.

> *On screen:* The deployment scales to 12 pods and a second m5.large joins with six pods on each node.

[LIVE] Scaling to 12 pods exceeded one m5.large, so Karpenter launched a second m5.large and the pods ended up six per node. Each new batch of pending pods gets its own fitting decision.

**[07:22]** Scale back to 5: the 5 pods fit on node 1, node 2 is empty.

> *On screen:* The deployment scales back to 5; node 1 holds all five pods and node 2 is left empty.

[LIVE] Scaling back to 5 replicas left pods that all fit on node 1, so node 2 became empty (or was emptied as replicas were removed). An empty node is the simplest consolidation case.

**[07:25]** After consolidateAfter (1 min) plus evaluation: about 70 s after the scale-down...

> *On screen:* A timer runs through consolidateAfter (1 min) plus evaluation, about 70 s.

With `consolidateAfter: 1m`, Karpenter waits one minute after the last pod change before considering a node for consolidation, then evaluates it. [LIVE] About 70 s after the scale-down, node 2 was selected for removal.

**[07:30]** ...node 2 was tainted and removed in about 22 s. 5 pods, 0 moved.

> *On screen:* Node 2 is tainted and removed in about 22 s while the five pods stay where they are.

[LIVE] Karpenter tainted node 2 (`karpenter.sh/disrupted`) so nothing new would land there, then drained and terminated it; from taint to gone took about 22 s. No pods had to move because the node was already empty.

**[07:34]** Node 1 stays: already the cheapest fit. That message is a result, not an error.

> *On screen:* Node 1 stays, with an 'Unconsolidatable: already cheapest' result label.

Node 1 stays because it is already the cheapest shape that holds the remaining five pods. Karpenter reports this as 'Unconsolidatable', which is a decision result, not an error. Seeing it in events means consolidation looked and found nothing cheaper.

### Key takeaways  `[07:44]`

- Karpenter launches single nodes for pending pods: no node groups
- NodePool = what is allowed; EC2NodeClass = AWS details
- Live: one m5.large, 5 pods Running in 34 s
- Empty node consolidated about 70 s after scale-down

---

## Chapter 6 — Fargate: serverless pods

**Starts at 07:58** · length 01:22 · source `C06-fargate` · hook: *"No nodes to run: every pod gets its own micro-VM"*

**What you'll learn.** This chapter follows `concepts/compute/06-fargate/` (profile, scheduling, sizing, scaling and cleanup) and `labs/14-compute-fargate.md`. It shows how EKS decides a pod runs on Fargate, why the label must be on the pod template, how requests are rounded up to a Fargate size, and that each pod becomes its own node. Executed live; profile ACTIVE in 76 s.

### How a pod lands on Fargate

**[08:03]** AWS-run webhooks in the control plane check each new pod against your Fargate profiles.

> *On screen:* A pod enters the control plane, passes AWS-run webhooks and is compared against Fargate profile cards.

Fargate runs pods without nodes you manage. When a pod is created, an AWS-run mutating webhook and scheduler logic in the EKS control plane compare it with your Fargate profiles; you do not install anything in the cluster for this. The decision is made at pod creation time only.

**[08:07]** Match: fargate-scheduler builds a micro-VM for it. No match: a normal EC2 node.

> *On screen:* A matching pod is routed to fargate-scheduler and a micro-VM; a non-matching pod goes to a regular EC2 node.

If the pod matches a profile, it is assigned to `fargate-scheduler` instead of the default scheduler, and AWS starts a dedicated micro-VM for it; the pod's node shows up with the label `eks.amazonaws.com/compute-type=fargate`. If it matches no profile, it is scheduled normally onto EC2 nodes. Fargate pods cannot use DaemonSets, privileged mode or most host-level features [BG].

### Create a Fargate profile (live)

**[08:16]** A profile = selectors (namespace + labels), private subnets and a pod execution role.

> *On screen:* A Fargate profile card appears with namespace/label selectors, private subnets and a pod execution role.

A Fargate profile contains selectors (a namespace, optionally plus labels), the private subnets Fargate pods use, and a pod execution IAM role that lets the Fargate agent pull images and write logs. Pods on Fargate get their own ENI and IP in those private subnets [W]. Profiles are immutable: to change one, create a new profile and delete the old one [BG].

**[08:21]** Live: CREATING to ACTIVE in 76 s.

> *On screen:* The profile status changes from CREATING to ACTIVE with a 76 s timer.

[LIVE] The profile moved from CREATING to ACTIVE in 76 s. Creating or deleting profiles is serialised per cluster, so batch scripts that create several profiles must wait for each one.

### Scheduling: the label goes on the pod template

**[08:27]** The profile already existed, but checkout stayed on EC2: it had no fargate=yes label.

> *On screen:* The checkout pod sits on an EC2 node despite the profile, with a missing fargate=yes label highlighted.

[LIVE] The profile selected the checkout namespace with the label `fargate=yes`, but the checkout pods kept running on EC2. Existing pods are never moved, and these pods did not carry the label anyway. Matching happens only when a pod is created.

**[08:32]** Add the label to the pod template: a new pod is created and matches the profile.

> *On screen:* The label is added to the pod template and a new checkout pod is created, matching the profile.

The label must go on the pod template (`spec.template.metadata.labels`), not on the Deployment's own metadata. Patching the template triggers a rollout, which creates new pods; those new pods carry `fargate=yes`, match the profile, and are sent to Fargate.

**[08:35]** Live: rollout 58 s (VM ~35 s + image pull ~15 s). redis has no label: stays on EC2.

> *On screen:* The new pod moves to a Fargate micro-VM in 58 s, while redis stays on EC2.

[LIVE] The rollout took 58 s, roughly 35 s to start the micro-VM and about 15 s for the image pull. The checkout redis pod has no `fargate=yes` label, so it stayed on EC2. This shows you can split one namespace between Fargate and EC2 with labels.

### Sizing: requests rounded UP to the Fargate menu

**[08:42]** Fargate sums the requests, adds overhead, and rounds up to the next size on its menu.

> *On screen:* Requested CPU and memory are summed, overhead is added and the result snaps up to the next Fargate size.

Fargate adds up the pod's container requests, adds overhead for the Kubernetes components it runs in the VM (about 256 MB of memory [BG]), and rounds up to the nearest supported vCPU/memory combination. Limits are not used for sizing; requests are. [LIVE] 1 CPU / 2.5G of requests became 1 vCPU / 3 GB.

**[08:47]** 512Mi became 1 GB here. You pay for what is provisioned: request what you need.

> *On screen:* 512Mi is shown becoming 1 GB, with a 'you pay for what is provisioned' note.

[LIVE] 250m CPU and 512Mi memory became 0.25 vCPU and 1 GB (the workshop page shows 0.5 GB for the same request; the live result was 1 GB). You are billed for the provisioned size, so oversized requests cost money directly. Check the actual size in the pod annotation `CapacityProvisioned`, which is where the source read these values.

### Scaling: one pod = one node (live)

**[08:53]** 3 replicas = 3 separate Fargate nodes, ready in 70 s. Scaling pods is scaling compute.

> *On screen:* Three checkout replicas appear on three separate Fargate nodes within 70 s.

[LIVE] Scaling checkout to 3 replicas produced 3 separate Fargate nodes, ready in about 70 s. On Fargate, each pod is its own node, so scaling pods is scaling compute; there is no Cluster Autoscaler or Karpenter involved.

**[08:59]** Cleanup: checkout back on EC2, profile deleted in about 93 s, role removed.

> *On screen:* Checkout moves back to EC2, the profile is deleted after about 93 s and the role is removed.

[LIVE] Cleanup removed the label so checkout returned to EC2, deleted the profile (about 93 s), and removed the pod execution role. Delete the profile only after the pods have left Fargate, otherwise running Fargate pods are terminated with it [BG].

### Key takeaways  `[09:04]`

- A profile (namespace + labels) decides which pods go to Fargate
- fargate-scheduler gives each pod its own micro-VM node
- Requests are rounded up: 250m/512Mi became 0.25 vCPU / 1 GB
- Live: profile ACTIVE in 76 s; 3 replicas = 3 nodes

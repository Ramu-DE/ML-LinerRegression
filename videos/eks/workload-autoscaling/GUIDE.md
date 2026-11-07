# AWS EKS — Workload Autoscaling — Guide

Total length: **05:13**

**Video:** [`EKS-Workload-Autoscaling.mp4`](EKS-Workload-Autoscaling.mp4), 1920×1080, 30 fps, with chapter markers. In VLC use *Playback → Chapter*.
**Editable drawings:** [`EKS-Workload-Autoscaling.excalidraw`](EKS-Workload-Autoscaling.excalidraw). Open it at excalidraw.com with *Menu → Open*; each scene is a named frame.
**Source:** `EKS/AWS_EKS_fundamentals/`. Chapters follow the numbered files in `concepts/workload-autoscaling/` (hpa, cluster-proportional-autoscaler, keda), `labs/15–17` and `labs/_cluster-upgrades-note.md`, in order.

**Execution status:** **Documented only.** HPA, CPA and KEDA were not executed live. Numbers come from the workshop's sample output, never from a measurement.

### How to use this guide
- Each **[mm:ss]** line is the on-screen caption, with its exact time in this video.
- *On screen* describes the animation; the paragraph under it explains the idea and the kubectl/YAML/AWS pieces involved.
- Tags follow the source notes: **[LIVE]** = measured on a real EKS cluster, **[W]** = stated by the EKS Workshop, **[BG]** = background knowledge (verify before relying on it). Account IDs and IPs are never shown.

## Chapters

| Starts | Chapter | Length | Source video |
|---|---|---|---|
| 00:00 | [Introduction](#introduction) | 00:12 | `00-intro` |
| 00:12 | [Chapter 1 — Horizontal Pod Autoscaler](#chapter-1--horizontal-pod-autoscaler) | 01:19 | `W01-hpa` |
| 01:32 | [Chapter 2 — Cluster Proportional Autoscaler](#chapter-2--cluster-proportional-autoscaler) | 01:32 | `W02-cpa` |
| 03:04 | [Chapter 3 — KEDA: event-driven autoscaling](#chapter-3--keda-event-driven-autoscaling) | 01:22 | `W03-keda` |
| 04:27 | [Chapter 4 — EKS Cluster Upgrades](#chapter-4--eks-cluster-upgrades) | 00:45 | `W04-cluster-upgrades-note` |

---

## Introduction

**Starts at 00:00** · length 00:12 · source `00-intro` · hook: *"Scaling pods, not nodes: HPA, CPA and KEDA"*

**What you'll learn.** This short opening lists the four chapters: Horizontal Pod Autoscaler, Cluster Proportional Autoscaler, KEDA, and a note on cluster upgrades. It follows `concepts/workload-autoscaling/README.md` and `labs/15`–`17`. The whole topic is **documented only**: it is built from the EKS Workshop text and was not executed live, so no number in this video is a measurement.

### What this video covers

**[00:07]** Documented from the workshop text; not executed live.

> *On screen:* The four numbered agenda items type in one by one, then this caption appears underneath.

Unlike the Exposing, Storage and Compute videos, nothing here was run on a cluster, so the outputs you will see are the workshop's own sample outputs. Workload autoscaling changes the number of **pods**; node autoscaling (Cluster Autoscaler, Karpenter) changes the number of **nodes**. The two work together: new pods that don't fit trigger new nodes.


---

## Chapter 1 — Horizontal Pod Autoscaler

**Starts at 00:12** · length 01:19 · source `W01-hpa` · hook: *"Add pods when they get busy, remove them when idle"*

**What you'll learn.** How the Horizontal Pod Autoscaler (HPA) adds and removes replicas of a Deployment based on CPU. It follows `concepts/workload-autoscaling/hpa/README.md` and `labs/15-workload-hpa.md`, in the lab's order: Metrics Server, CPU requests, the HPA object, then a load test. **Documented only** — the replica numbers are the workshop's sample output, not a live run. Prerequisite: the controller idea from the Exposing video.

### The pieces of the HPA loop

**[00:18]** Metrics Server collects CPU and memory per pod from the kubelets.

> *On screen:* Kubelet boxes on each node send CPU/memory numbers into a Metrics Server box.

Metrics Server scrapes each kubelet and serves the resource metrics API (`metrics.k8s.io`), which is what `kubectl top` and the HPA read. On EKS it is **not installed by default**: it is an add-on, and the workshop installs it as a community add-on. You can check it with `kubectl -n kube-system get pod -l app.kubernetes.io/name=metrics-server`. Without it, a CPU-based HPA has nothing to read.

**[00:21]** The HPA controller reads those numbers and edits spec.replicas of the Deployment.

> *On screen:* An arrow runs from Metrics Server to an HPA controller box, which then edits the Deployment's spec.replicas.

The HPA does not start or stop pods itself. It only changes one field, `spec.replicas`, on the target Deployment; the Deployment and ReplicaSet controllers then create or delete pods to match. That is why an HPA works the same way for any scalable resource (Deployment, StatefulSet).

**[00:24]** It is the same controller pattern as everywhere in Kubernetes: desired vs current.

> *On screen:* The arrows close into a loop: metrics → HPA → replicas → pods → metrics.

This is the same reconcile pattern as the AWS Load Balancer Controller: compare desired state with current state and act on the difference, over and over. The HPA re-evaluates on a fixed interval [BG: about every 15 s by default], so it reacts to load changes within seconds to minutes, not instantly.

### Utilization is measured against the CPU request

**[00:30]** In the lab the ui pod requests 250m CPU (the lab also sets a 250m limit).

> *On screen:* A ui pod card shows `requests: cpu 250m` and a usage bar filling against that 250m line (illustrative usage).

CPU utilisation in an HPA means **usage ÷ request**, not usage ÷ node capacity. The lab patches the `ui` Deployment to add `resources.limits.cpu: 250m`; the request of 250m CPU (and 1.5Gi memory) was already set. So a pod using 200m is at 80% of its request — the usage value on screen is illustrative.

**[00:35]** No request means no percentage: the HPA shows <unknown> and does nothing.

> *On screen:* The request line disappears and the HPA status changes to `<unknown>/80%`.

With no CPU request there is no denominator, so `kubectl get hpa` shows `<unknown>` for the target and the HPA never scales. This is the most common reason an HPA "does nothing". Always set CPU requests on any workload you want to autoscale on CPU.

### The HPA object from the lab

**[00:41]** One replica minimum, four maximum, target 80% average CPU across the ui pods.

> *On screen:* The HPA YAML card from the lab appears with min 1, max 4 and target 80% highlighted.

The lab object uses `autoscaling/v1` with `minReplicas: 1`, `maxReplicas: 4` and `targetCPUUtilizationPercentage: 80`, scaling the `ui` Deployment. The HPA aims to keep the **average** CPU across all ui pods at 80% of their requests. `maxReplicas` is a hard ceiling: even under heavy load it will not go past 4.

### Generate load, watch the HPA (workshop sample)

**[00:47]** The load generator sends about 50 requests per second to the ui Service.

> *On screen:* A load-generator pod starts sending request arrows to the ui Service.

The workshop runs `kubectl run load-generator --image=williamyeh/hey:latest --restart=Never -- -c 10 -q 5 -z 60m http://ui.ui.svc/home`. `-c 10` is 10 concurrent workers and `-q 5` is 5 requests per second each, so about 50 requests per second for up to 60 minutes. The traffic stays inside the cluster, through the ui Service.

**[00:50]** desired replicas = ceil(current replicas × current CPU% / target%)

> *On screen:* The formula writes itself out, then is evaluated row by row on the workshop sample values.

desiredReplicas = ceil(currentReplicas × currentUtilization / targetUtilization) [BG]. From the workshop sample: 1 replica at 99% gives ceil(1 × 99/80) = ceil(1.24) = 2; 2 replicas at 89% gives ceil(2.23) = 3. At 3 replicas and 84%, 84/80 = 1.05 is inside the HPA's roughly 10% tolerance [BG], so it stays at 3.

**[01:00]** Replicas climb 1 → 2 → 3 while average CPU sits above 80%, then load is shared.

> *On screen:* The replica count steps 1 → 2 → 3 as new pod boxes appear and the average CPU bar drops back toward 80%.

Each new replica takes a share of the same ~50 requests per second, so the average utilisation falls. The workshop's sample watch shows `69%/80%` at 1 replica, then `99%/80%`, then replicas 2 at 89% and replicas 3 at 84%. It never reaches the max of 4 because 3 pods are enough to hold CPU near the target.

**[01:06]** Stop the load: after a 5-minute stabilisation window [BG] the HPA returns to 1.

> *On screen:* The load generator is removed and, after a waiting timer, the replicas shrink back to 1.

Stop the load with `kubectl delete pod load-generator`. Scale-up is fast, but scale-down waits a stabilisation window of about 5 minutes by default [BG], so a short dip in traffic doesn't throw pods away that you'd need again a moment later. Then the HPA returns the Deployment to `minReplicas: 1`.

### Where the HPA hands over

**[01:12]** HPA scales pods; when pods don't fit, the node autoscalers take over.

> *On screen:* New pods that don't fit on existing nodes turn Pending, and an arrow hands over to Cluster Autoscaler / Karpenter boxes.

The HPA only asks for more pods; it never checks whether the nodes have room. If the scheduler can't place a new replica, the pod stays Pending, and that Pending pod is exactly the signal Cluster Autoscaler or Karpenter react to (see the Compute video). Pod autoscaling and node autoscaling are separate loops that chain together.

### Key takeaways  `[01:17]`

- Metrics Server → HPA controller → Deployment replicas
- Utilization = usage ÷ CPU request (no request = <unknown>)
- desired = ceil(replicas × current% / target%)
- This lab is documented from the workshop text, not run live

---

## Chapter 2 — Cluster Proportional Autoscaler

**Starts at 01:32** · length 01:32 · source `W02-cpa` · hook: *"Scale with the size of the cluster, not with the load"*

**What you'll learn.** The Cluster Proportional Autoscaler (CPA) sizes a workload by **cluster size** — nodes and cores — instead of by load. It follows `concepts/workload-autoscaling/cluster-proportional-autoscaler/README.md` and `labs/16-workload-cpa.md`: what CPA is, linear mode, the CoreDNS lab, ladder mode, and CPA vs HPA. **Documented only**; the lab replica counts come from the workshop text.

### It counts nodes and cores

**[01:37]** CPA polls the API server for schedulable nodes and cores, and resizes a target workload.

> *On screen:* A CPA pod polls the API server box, which returns a node count and a core count.

CPA is a small Deployment running a Go API client. On every poll interval it asks the API server how many schedulable nodes and cores exist, re-reads its ConfigMap, and resizes the target workload. Typical targets are platform services that must grow with the cluster, such as CoreDNS.

**[01:41]** It measures nothing: no Metrics Server. Configured by flags and a ConfigMap, not a K8s object.

> *On screen:* A crossed-out Metrics Server icon appears next to a ConfigMap card and command-line flags.

CPA does not use the Metrics API, Metrics Server or a Prometheus adapter — it never looks at how busy pods are. It is configured by **flags plus a ConfigMap**, not by a Kubernetes resource like `HorizontalPodAutoscaler`, so you won't find it with `kubectl get hpa`.

### Linear mode: replicas in proportion

**[01:48]** Take whichever ratio needs more replicas, then clamp between min and max.

> *On screen:* The linear formula appears, with the two ratios computed side by side and the larger one winning before min/max clamps.

Linear mode: replicas = max( ceil(cores / coresPerReplica), ceil(nodes / nodesPerReplica) ), then clamped to [min, max]. Either ratio may be omitted, and both are floats. The workshop's example ConfigMap key `linear` is `{"coresPerReplica":2,"nodesPerReplica":1,"min":1,"max":100,...}`.

**[01:51]** Two safety switches: never a single replica on a multi-node cluster, and count all nodes.

> *On screen:* Two switch icons light up: preventSinglePointFailure and includeUnschedulableNodes.

`preventSinglePointFailure: true` forces at least 2 replicas whenever the cluster has more than one node. `includeUnschedulableNodes: true` counts cordoned and draining nodes too; the default (false) counts only schedulable nodes, which would shrink the target during a node rollout.

### Lab: autoscale CoreDNS (workshop text)

**[01:57]** One CoreDNS replica per 2 nodes, minimum 2, maximum 6.

> *On screen:* The lab ConfigMap card shows nodesPerReplica 2, min 2, max 6.

In the lab, CPA targets CoreDNS (`deployment coredns` in `kube-system`, pods labelled `k8s-app=kube-dns`) with `linear: {nodesPerReplica: 2, min: 2, max: 6, preventSinglePointFailure: true, includeUnschedulableNodes: true}`. No core ratio is set, so only the node count matters.

**[02:02]** With 3 nodes the workshop shows 2 CoreDNS pods.

> *On screen:* Three node boxes appear with two CoreDNS pods across them.

With 3 nodes: ceil(3 / 2) = 2, which also equals the minimum of 2, so CoreDNS runs 2 replicas, as the workshop shows. The minimum matters most on small clusters, where DNS availability is critical.

**[02:06]** Grow the node group by two. CPA sees 5 nodes on its next poll.

> *On screen:* Two more node boxes slide in, and the CPA poll arrow reads 5 nodes.

The lab grows the managed node group by two nodes. CPA doesn't watch for events; it notices the change on its next poll of the API server, so there is a short delay between the nodes becoming Ready and CoreDNS resizing.

**[02:09]** CoreDNS goes from 2 to 3 replicas — one per two nodes.

> *On screen:* A third CoreDNS pod pops in and a CPA log line "updating replicas from 2 to 3" appears.

With 5 nodes: ceil(5 / 2) = ceil(2.5) = 3, inside [2, 6], so CPA sets CoreDNS to 3 replicas. CPA writes the replica count directly on the Deployment; if you also attached an HPA to the same Deployment, the two would fight over `spec.replicas`.

### Same rule, other cluster sizes

**[02:20]** min protects availability on tiny clusters; max stops runaway growth on big ones.

> *On screen:* A table fills in node counts 1/4/9/20 with the resulting replicas 2/2/5/6.

Applying the same lab rule: 1 node → ceil(0.5) = 1, raised to min 2; 4 nodes → 2; 9 nodes → ceil(4.5) = 5; 20 nodes → 10, capped at max 6. So `min` protects availability on tiny clusters and `max` stops runaway growth on large ones.

### Ladder mode: a step function

**[02:25]** The workshop's ladder ConfigMap: 1 core → 1 replica, 64 → 3, … up to 4096 cores → 15.

> *On screen:* A step chart draws the ladder ConfigMap: cores on the x-axis, replicas jumping at each threshold.

Ladder mode is a lookup table instead of a ratio. The workshop example is `coresToReplicas: [[1,1],[64,3],[512,5],[1024,7],[2048,10],[4096,15]]` and `nodesToReplicas: [[1,1],[2,2]]`; the table giving more replicas wins. Unlike linear mode, ladder entries can be 0, which lets an optional feature switch on only when the cluster grows large enough.

### CPA vs HPA

**[02:38]** HPA reacts when pods get busy; CPA reacts when the cluster grows or shrinks.

> *On screen:* A two-column comparison appears: HPA triggered by busy pods, CPA by cluster size.

HPA answers "are my pods overloaded?" using metrics; CPA answers "has the cluster changed size?" using node and core counts. For DNS, the cluster's size is a good proxy for how many clients will query it, so CPA fits better than CPU-based scaling.

**[02:43]** This lab is educational: the workshop recommends the CoreDNS add-on autoscaling for production.

> *On screen:* A note card points to the CoreDNS EKS add-on as the production option.

The workshop calls this lab educational and its config a demo, not a best practice. On EKS, CoreDNS can be autoscaled by the CoreDNS **EKS add-on** itself, which the workshop recommends for production. CPA is still useful for your own platform services that should grow with the cluster.

### Key takeaways  `[02:48]`

- CPA scales replicas by node / core count — no metrics
- Linear: max of the two ratios, clamped to [min, max]
- Lab: nodesPerReplica 2 → 3 nodes = 2, 5 nodes = 3 CoreDNS
- Documented from the workshop text, not run live

---

## Chapter 3 — KEDA: event-driven autoscaling

**Starts at 03:04** · length 01:22 · source `W03-keda` · hook: *"Scale on signals that live outside the pod"*

**What you'll learn.** KEDA (Kubernetes Event-Driven Autoscaling) lets you scale on signals outside the pod, such as an ALB request rate in CloudWatch. It follows `concepts/workload-autoscaling/keda/01`–`05` and `labs/17-workload-keda.md`: concepts, installation, the Ingress it depends on, the ScaledObject, and the load test. **Documented only**; the replica numbers are the workshop's sample output. It builds on the HPA chapter and on Ingress/ALB from the Exposing video.

### Why not just the HPA?

**[03:14]** Sometimes the right signal is queue length or request rate — outside the pod.

> *On screen:* An HPA box with only CPU/memory inputs is shown next to an HPA+KEDA box fed by queues, request rates and other external sources.

A plain HPA only sees resource metrics (CPU, memory) unless you install a custom/external metrics adapter. KEDA is that adapter plus an operator: it pulls metrics from external systems (CloudWatch here) and exposes them to an HPA. It also allows `minReplicaCount: 0`, which a plain HPA can't do.

### KEDA installs three deployments

**[03:21]** Installed with Helm. The operator gets an IAM role through IRSA to read CloudWatch.

> *On screen:* Three deployment boxes pop in — keda-operator, keda-operator-metrics-apiserver and keda-admission-webhooks — with an IAM role badge on the operator.

KEDA is installed with Helm. The operator watches ScaledObjects and drives scaling, the metrics API server serves external metrics to the HPA, and the admission webhooks validate KEDA objects. The lab gives the operator an IAM role with `CloudWatchReadOnlyAccess` through IRSA (`podIdentity.aws.irsa.enabled=true`), trusted for ServiceAccount `keda:keda-operator`.

### The lab: scale ui on an ALB metric

**[03:27]** Users hit the ALB that the Ingress created; it forwards to the ui pods.

> *On screen:* User arrows flow into an ALB box and on to the ui pods.

The scaling signal is an ALB metric, so the lab first validates that the `ui` Ingress has created an ALB (`03-validating-the-ingress.md`). No ALB means no metric and nothing to scale on. The Ingress/ALB pages themselves were executed live in the Exposing chapter, but this KEDA lab was not.

**[03:30]** The ALB publishes RequestCountPerTarget to CloudWatch.

> *On screen:* A metric arrow leaves the ALB and lands in a CloudWatch box labelled RequestCountPerTarget.

The ALB publishes `RequestCountPerTarget` in the `AWS/ApplicationELB` namespace: requests per registered target. Because it is per target, it's a natural per-pod load signal for a Deployment behind the ALB.

**[03:33]** The keda-operator reads the ScaledObject and polls CloudWatch every 30 seconds.

> *On screen:* The keda-operator reads a ScaledObject card and a polling arrow ticks toward CloudWatch every 30 s.

The ScaledObject sets `pollingInterval: 30`, so KEDA queries CloudWatch every 30 seconds. CloudWatch metrics themselves arrive with some delay, so KEDA scaling on AWS metrics reacts in tens of seconds to minutes — fine for request bursts, too slow for millisecond spikes [BG].

**[03:36]** KEDA creates the HPA keda-hpa-ui-hpa and feeds it the metric. The HPA sets replicas.

> *On screen:* KEDA creates an HPA box named keda-hpa-ui-hpa, which then sets the replicas on the ui Deployment.

KEDA doesn't replace the HPA — it creates one (`keda-hpa-ui-hpa`) and feeds it the external metric, so the usual HPA formula and stabilisation rules still apply. That means you should not also create your own HPA for the same Deployment; the two would compete.

### The ScaledObject (workshop manifest, shortened)

**[03:42]** The trigger is a CloudWatch Metrics Insights query on the ALB's target group.

> *On screen:* The ScaledObject YAML card appears with callouts on the trigger query, target value 100, min 1 / max 10 and identityOwner: operator.

The trigger is a CloudWatch Metrics Insights query: `SELECT COUNT(RequestCountPerTarget) FROM SCHEMA("AWS/ApplicationELB", LoadBalancer, TargetGroup) WHERE TargetGroup = ... AND LoadBalancer = ...`, with `targetMetricValue: "100"` per pod. `minReplicaCount: 1`, `maxReplicaCount: 10`, `cooldownPeriod: 300`, and `identityOwner: operator` means "use the operator's own IRSA identity" rather than a TriggerAuthentication.

### Generate load, watch the HPA (workshop sample)

**[03:51]** Kubernetes writes quantities in milli-units: 194500m means 194.5.

> *On screen:* The value 194500m converts to 194.5 on screen.

Kubernetes quantities use milli-units, so `kubectl get hpa` may print `194500m/100`, which is 194.5 requests per target against a target of 100. Reading it as 194,500 is a common misreading. In the workshop sample the metric rises from 7/100 to 778/100 to 194500m/100 as the load runs.

**[04:02]** In the workshop sample, replicas step 1 → 4 → 8 → 10 while the load runs.

> *On screen:* The replica counter steps 1 → 4 → 8 → 10 and stops at the max line.

In the workshop sample, replicas go 1 → 4 → 8 → 10. The 4 → 8 step matches the HPA formula: ceil(4 × 194.5 / 100) = ceil(7.78) = 8. It then reaches `maxReplicaCount: 10` and stays there. The first 1 → 4 step is smaller than the formula alone would give, likely because of HPA scale-up rate limits, which the source doesn't cover.

### Scale down — and scale to zero

**[04:08]** This lab keeps minimum 1; zero is possible with KEDA, unlike a plain HPA.

> *On screen:* With the load removed, replicas fall back to 1; a dashed path shows how minReplicaCount 0 would go all the way to zero.

When the load stops, the HPA scales down after its stabilisation window. This lab keeps `minReplicaCount: 1`. With `minReplicaCount: 0`, KEDA itself handles the final 1 → 0 step after `cooldownPeriod` (300 s here) with no active trigger — that's how KEDA can save cost for idle workloads, which a plain HPA can't.

### Key takeaways  `[04:14]`

- KEDA scales on external events (60+ scalers)
- You write a ScaledObject; KEDA creates and feeds an HPA
- Lab: ALB RequestCountPerTarget in CloudWatch, target 100
- Documented from the workshop text, not run live

---

## Chapter 4 — EKS Cluster Upgrades

**Starts at 04:27** · length 00:45 · source `W04-cluster-upgrades-note` · hook: *"No lab here — but the clock is always ticking"*

**What you'll learn.** A short, honest note on EKS cluster upgrades. It follows `labs/_cluster-upgrades-note.md`: the workshop's Fundamentals section has **no upgrade lab**, only a page pointing to a separate EKS Upgrades Workshop. Facts from that page are tagged [W]; the upgrade order at the end is [BG] background to verify against AWS docs.

### Why upgrades never stop [W]

**[04:32]** A new Kubernetes minor version arrives about every 4 months, supported for about 12.

> *On screen:* Version bars appear on a timeline, roughly every 4 months, each with a ~12-month support span (illustrative versions).

The workshop states that Kubernetes ships a new minor version roughly every four months and each is supported for about twelve months [W]. The bars on screen only illustrate that cadence; they are not real version numbers. Staying current is not optional — an unsupported version eventually has to be upgraded.

**[04:36]** So EKS users must plan and execute upgrades on a regular cadence.

> *On screen:* A repeating calendar loop appears: plan → upgrade → verify.

Because releases keep coming, upgrades should be a routine, scheduled process rather than an occasional emergency [W]. In practice that means rehearsing in a non-production cluster first and keeping workloads ready for node replacement (replicas ≥ 2 and PodDisruptionBudgets for critical apps) [BG].

### The workshop points elsewhere [W]

**[04:43]** Fundamentals has no upgrade lab; it links to a separate EKS Upgrades Workshop.

> *On screen:* A link card points to the external EKS Upgrades Workshop with its four stages, plus pointers to MNG AMI upgrades and Karpenter drift.

The external workshop covers preparation → choosing an upgrade plan → executing the upgrade → maintaining availability [W]. Inside Fundamentals, the related mechanics are the managed node group AMI upgrade (setup → scale up → upgrade → scale down, honouring PDBs) and Karpenter's node refresh through `expireAfter` and Drift, both covered in the Compute video.

### The usual order [BG — verify in AWS docs]

**[04:54]** Background order, not from the workshop page: control plane, then add-ons, then nodes.

> *On screen:* Five boxes chain left to right: pre-checks, control plane, add-ons, data plane, post-checks, with a [BG] badge.

[BG — verify in AWS docs] The usual order: pre-checks (deprecated APIs, add-on compatibility, EKS Upgrade Insights, free subnet IPs), then the control plane one minor version at a time, then add-ons such as VPC CNI, CoreDNS, kube-proxy and CSI drivers, then the data plane (MNG `update-nodegroup-version`, Karpenter drift, restarting Fargate pods), then post-checks. Nodes must not lag the control plane by more than the allowed version skew.

### Key takeaways  `[05:01]`

- Minor versions ~every 4 months, ~12 months support [W]
- No lab in Fundamentals: see the EKS Upgrades Workshop
- Order [BG]: control plane → add-ons → data plane

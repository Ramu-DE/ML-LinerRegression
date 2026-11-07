# AWS EKS — Networking — Guide

Total length: **08:47**

**Video:** [`EKS-Networking.mp4`](EKS-Networking.mp4), 1920×1080, 30 fps, with chapter markers. In VLC use *Playback → Chapter*.
**Editable drawings:** [`EKS-Networking.excalidraw`](EKS-Networking.excalidraw). Open it at excalidraw.com with *Menu → Open*; each scene is a named frame.
**Source:** `EKS/AWS_EKS_fundamentals/`. Chapters follow the numbered files in `concepts/networking/` (01 … 07, plus the cheatsheet and lab-by-lab flows), in order.

**Execution status:** **Partly executed** on an EKS Auto Mode cluster (K8s 1.35): pod IPs, traffic paths and a NetworkPolicy test (accepted but **not enforced** there). Security groups for pods, custom networking, prefix delegation and hybrid nodes are **documented only**; each chapter shows its status.

### How to use this guide
- Each **[mm:ss]** line is the on-screen caption, with its exact time in this video.
- *On screen* describes the animation; the paragraph under it explains the idea and the kubectl/YAML/AWS pieces involved.
- Tags follow the source notes: **[LIVE]** = measured on a real EKS cluster, **[W]** = stated by the EKS Workshop, **[BG]** = background knowledge (verify before relying on it). Account IDs and IPs are never shown.

## Chapters

| Starts | Chapter | Length | Source video |
|---|---|---|---|
| 00:00 | [Introduction](#introduction) | 00:12 | `00-intro` |
| 00:12 | [Chapter 1 — How pods get IP addresses](#chapter-1--how-pods-get-ip-addresses) | 01:20 | `N01-pod-ip-addresses` |
| 01:32 | [Chapter 2 — How pods communicate](#chapter-2--how-pods-communicate) | 01:19 | `N02-pod-communication` |
| 02:52 | [Chapter 3 — Network Policies](#chapter-3--network-policies) | 01:19 | `N03-network-policies` |
| 04:12 | [Chapter 4 — Security Groups for Pods](#chapter-4--security-groups-for-pods) | 01:09 | `N04-security-groups-for-pods` |
| 05:21 | [Chapter 5 — Custom Networking](#chapter-5--custom-networking) | 01:07 | `N05-custom-networking` |
| 06:29 | [Chapter 6 — Prefix Delegation](#chapter-6--prefix-delegation) | 01:13 | `N06-prefix-delegation` |
| 07:43 | [Chapter 7 — EKS Hybrid Nodes](#chapter-7--eks-hybrid-nodes) | 01:04 | `N07-hybrid-nodes` |

---

## Introduction

**Starts at 00:00** · length 00:12 · source `00-intro` · hook: *"How every pod gets a real VPC IP address"*

**What you'll learn.** This short opening lists the seven networking chapters in the order of the source folder `concepts/networking/` (files 01–07). It also sets expectations about evidence: only parts of this topic were executed live, on an EKS Auto Mode cluster running Kubernetes 1.35; everything else is the workshop text [W] or background [BG], and each chapter says which.

### What this video covers

**[00:07]** Partly executed on an EKS Auto Mode cluster; documented-only parts are marked.

> *On screen:* The seven numbered chapter titles pop in down two columns, then the caption about what was and was not executed types in underneath.

Networking is the one topic in this repo that was only partly executed. The live work (pod IPs, traffic paths and a NetworkPolicy test) ran on an EKS Auto Mode cluster, where AWS manages the VPC CNI for you and hides the usual `aws-node` DaemonSet. Security groups for pods, custom networking, prefix delegation and hybrid nodes need a standard VPC CNI or extra infrastructure, so they are documented from the workshop text only. Watch for the [LIVE], [W] and [BG] tags in each chapter.


---

## Chapter 1 — How pods get IP addresses

**Starts at 00:12** · length 01:20 · source `N01-pod-ip-addresses` · hook: *"Why does every pod get a real VPC IP address?"*

**What you'll learn.** This chapter follows `concepts/networking/01-how-pods-get-ip-addresses.md`: the two-VPC layout, underlay mode, what happens when a pod is created, the warm pool, the max-pods formula and subnet exhaustion. The pod-level observations (a /32 address, gateway 169.254.1.1, MTU 9001, IPs from the node subnet) are [LIVE] from the Auto Mode cluster; the step-by-step ipamd flow and warm-pool settings are [BG] for a standard VPC CNI.

### Two VPCs, one cluster

**[00:19]** The control plane runs in an AWS-managed VPC. Your worker nodes run in YOUR VPC.

> *On screen:* Two boxes appear side by side: an AWS-managed VPC holding the EKS control plane and your VPC holding the worker nodes, joined by a connection line.

[W] Every EKS cluster spans two VPCs. AWS runs the control plane (API server, etcd) in a VPC it manages, while your worker nodes live in your own VPC. Nodes reach the API server through the public endpoint or through EKS-managed ENIs that EKS places in your subnets, and the API server uses those same ENIs to reach kubelets for `kubectl logs` and `exec`. The cluster used for the live tests had both public and private endpoint access enabled [LIVE].

**[00:24]** VPC CNI runs in underlay mode: a pod IP is a real VPC IP, with no overlay network.

> *On screen:* Pods appear inside a node within the VPC subnet, each labelled with an address from the same 10.98.x.x range as the node itself.

Underlay mode means the VPC CNI gives each pod a real secondary IP of the node's ENI, not an address on a private overlay network. The VPC therefore knows where every pod lives, so packets between pods travel with their real IPs and no tunnel or encapsulation is needed. A side effect [BG] is that security groups, route tables and VPC flow logs all see pod IPs directly. In the live cluster the VPC was 10.98.0.0/16 and pod IPs came from the node subnet 10.98.11.0/24 [LIVE].

### What happens when a pod is created

**[00:32]** ipamd keeps spare IPs ready: the warm pool. A new pod's request flows down to ipamd.

> *On screen:* A new-pod request flows down a chain of boxes (scheduler, kubelet, containerd, VPC CNI plugin) to ipamd, which holds a row of free IP slots: the warm pool.

[BG] When the scheduler binds a pod to a node, kubelet asks containerd to create the pod sandbox, and containerd calls the CNI plugin with a CNI ADD (pod name, namespace, network namespace). The plugin asks ipamd, the IP address management daemon in the `aws-node` pod, over a local gRPC call. ipamd keeps spare IPs already attached to the node's ENIs, so it can answer at once. This warm pool is why pod start-up does not wait for an EC2 API call.

**[00:38]** ipamd hands over a free IP at once: 10.98.11.132. No EC2 call on this path.

> *On screen:* One free slot in the warm pool lights up and the address 10.98.11.132 moves from ipamd into the new pod.

[BG] ipamd takes a free IP from the pool and hands it back to the plugin, which creates a veth pair: `eth0` inside the pod, the other end on the host. The pod gets a /32 address and the host gets a /32 route pointing at the veth. No EC2 call happens on this path, which keeps pod creation fast. The address 10.98.11.132 is the real IP the `client` test pod received on the live cluster [LIVE].

**[00:44]** [LIVE] The pod saw a /32 address, gateway 169.254.1.1 (the host answers), MTU 9001.

> *On screen:* A terminal-style card shows the pod's own view: eth0 with 10.98.11.132/32, default route via 169.254.1.1, and MTU 9001.

[LIVE] Inside the pod, `ip addr` showed a /32 address, so the pod is alone on its link and every packet must go through a gateway. That gateway, 169.254.1.1, is a link-local address that no real router owns: the host side of the veth simply answers ARP for it (proxy-ARP style [BG]), so every packet first goes to the node, which then routes it. MTU 9001 is the VPC's jumbo-frame size. The pod's DNS server was 172.20.0.10, inside the Service CIDR.

**[00:49]** ipamd refills the pool via EC2. Bigger pools: faster pods, but more subnet IPs held.

> *On screen:* ipamd sends a request up to an EC2 API box, and new free IP slots are added back into the warm pool.

[BG] In the background ipamd keeps the pool topped up with `AssignPrivateIpAddresses`, or by attaching a new ENI when the current ones are full. Its size is controlled on the `aws-node` DaemonSet: `WARM_ENI_TARGET` (default 1 spare ENI), `WARM_IP_TARGET`, `MINIMUM_IP_TARGET`, and `WARM_PREFIX_TARGET` in prefix mode. The trade-off is that every warm IP is taken out of your subnet even if no pod uses it, so a generous pool can exhaust a small subnet. On Auto Mode these knobs are hidden; the node's CNINode object shows `mode: dynamic` instead [LIVE].

### How many pods fit on one node?

**[00:57]** Without prefixes: m5.large has 3 ENIs × 10 IPs, so 29 pods. Karpenter reported 29.

> *On screen:* The max-pods formula builds on screen for an m5.large, 3 ENIs × (10 − 1) + 2 = 29, next to Karpenter's reported value of 29.

Without prefixes, `max pods = ENIs × (IPs per ENI − 1) + 2` [BG]. The −1 removes each ENI's own primary IP, and the +2 covers host-network pods such as `aws-node` and `kube-proxy`, which need no pod IP. For an m5.large that is 3 × 9 + 2 = 29, and Karpenter's NodePool status on the earlier workshop cluster reported exactly 29 pods for an m5.large [LIVE-earlier]. This is why small instance types fill up on IP addresses long before they run out of CPU or memory.

**[01:03]** Auto Mode node: formula 58, node allowed 56 (unexplained). Treat it as approximate.

> *On screen:* The same formula is applied to the Auto Mode c6a.xlarge, 4 × 14 + 2 = 58, beside the node's reported allocatable of 56, with a question mark between them.

[LIVE] The Auto Mode node was a c6a.xlarge, whose CNINode object reports 4 network interfaces and 15 IPv4 addresses per interface, so the formula gives 4 × 14 + 2 = 58. The node itself reported allocatable pods of 56. The source could not explain the gap of 2 (Auto Mode may reserve slots), so treat the formula as an approximation and check `kubectl describe node` for the real limit.

### Running out of pod IPs

**[01:10]** Pods use the node subnet. Fixes: bigger subnets, custom CIDRs, prefixes, IPv6.

> *On screen:* The node subnet's free-address bar drains as pods are added, and four fix cards appear: bigger subnets, custom CIDRs, prefix delegation and IPv6.

By default pods take IPs from the same subnet as the node's primary ENI [W], so many pods plus the warm pool can drain a small subnet, after which new pods fail with IP allocation errors. On the live cluster, 10.98.11.0/24 had 150 free addresses and 10.98.12.0/24 had 216 at the time [LIVE]. The fixes are to use larger subnets, move pods to a secondary CIDR (custom networking, chapter 5), pack IPs into /28 prefixes (prefix delegation, chapter 6), or run an IPv6 cluster [BG].

### Key takeaways  `[01:15]`

- A pod IP is a real VPC IP: underlay, no overlay
- ipamd hands pods IPs from a warm pool on the node ENIs
- Max pods = ENIs × (IPs per ENI − 1) + 2 (approximate)
- Small subnets run out: plan CIDRs, prefixes or custom networking

---

## Chapter 2 — How pods communicate

**Starts at 01:32** · length 01:19 · source `N02-pod-communication` · hook: *"Same node, other node, Service, internet: what really happens?"*

**What you'll learn.** This chapter follows `concepts/networking/02-how-pods-communicate.md` and traces every path a packet can take: pod to pod on the same and on different nodes, pod to Service, DNS, egress to the internet, and traffic coming in from a load balancer. The pod-to-pod, Service, DNS and NAT-gateway results are [LIVE] from a test namespace on the Auto Mode cluster (a `client` pod, a two-replica `web` Deployment and a `web` Service).

### Pod to pod: plain VPC routing

**[01:39]** [LIVE] client and one web pod share node 1; the second web pod runs on node 2.

> *On screen:* Two node boxes appear: node 1 holds the client pod and one web pod, node 2 holds the second web pod, each labelled with its 10.98.11.x address.

[LIVE] The test set-up was a Deployment `web` with two busybox httpd pods on port 8080, spread over two nodes, a ClusterIP Service `web` (172.20.114.222, port 80 → 8080) and a `client` pod. The client (10.98.11.132) happened to share node 1 with one web pod (10.98.11.134), while the other web pod (10.98.11.90) ran on node 2. That placement made it possible to test both the same-node and the cross-node path with one client.

**[01:46]** Same node: the packet goes to 169.254.1.1, and the host routes it to web's veth.

> *On screen:* A packet leaves the client, goes to the host at 169.254.1.1, and is routed down the web pod's veth on the same node.

On the same node the packet never leaves the machine [BG]. The client sends it to its gateway 169.254.1.1, which is the host, and the host's /32 route for 10.98.11.134 points straight at that pod's veth. `wget http://10.98.11.134:8080` returned `hello from web-…-nfp4m` [LIVE]. The reply travels back the same way.

**[01:54]** Other node: the VPC routes it ENI to ENI with the pod's own IP. No NAT, no tunnel.

> *On screen:* A packet leaves node 1's ENI with source 10.98.11.132, crosses the VPC fabric and enters node 2's ENI, where it is routed to the second web pod.

Across nodes the packet exits node 1's ENI with its real source IP, 10.98.11.132, with no NAT and no tunnel. The VPC fabric delivers it to 10.98.11.90 because that IP is registered as a secondary IP of node 2's ENI, and node 2's host route hands it to the pod's veth. `wget http://10.98.11.90:8080` returned `hello from web-…-zcjwr` [LIVE]. The same works across Availability Zones, though cross-AZ traffic is charged [BG], and the ENIs' security groups must allow it.

### Pod to Service: a virtual IP

**[02:03]** By name: the DNS server 172.20.0.10 answers with the Service IP 172.20.114.222.

> *On screen:* The client asks the DNS box at 172.20.0.10 for web.net-lab.svc.cluster.local and receives the Service IP 172.20.114.222.

[LIVE] `nslookup web.net-lab.svc.cluster.local` returned 172.20.114.222, and the DNS server 172.20.0.10 lies inside the Service CIDR 172.20.0.0/16. The pod's `/etc/resolv.conf` has `ndots:5`, so a short name like `web` is tried with each search suffix and resolves at once, while an external name with few dots is first tried against the cluster suffixes. On Auto Mode no `kube-dns` Service or CoreDNS pods were visible in the API, so DNS is provided by the platform. Remember that DNS is itself pod → Service traffic, so an egress NetworkPolicy must allow port 53.

**[02:10]** The node rewrites the virtual IP to a pod IP. [LIVE] 6 requests: zcjwr ×3, nfp4m ×3.

> *On screen:* The Service IP on the packet is rewritten on the node to one web pod's IP, and six request chips land on the two pods, three each.

A Service IP is virtual: no interface owns 172.20.114.222. Rules on the node rewrite the destination (DNAT) to one of the endpoints in the EndpointSlice, here 10.98.11.90 and 10.98.11.134, and rewrite the source of the reply back to the Service IP. [LIVE] Six requests by name returned zcjwr three times and then nfp4m three times, so both endpoints were used. The pattern is not strict round robin and should not be relied on [BG].

**[02:16]** Standard clusters use kube-proxy. Auto Mode had no kube-proxy pods, yet it worked.

> *On screen:* A kube-proxy box appears on a standard-cluster node, while the Auto Mode node shows no kube-proxy pods and the request still succeeds.

[BG] On a standard EKS cluster `kube-proxy` runs on every node and programs iptables or IPVS rules for these rewrites; the VPC CNI is not involved in this step. [LIVE] On the Auto Mode cluster no kube-proxy pods were visible, yet Service traffic worked, because Auto Mode runs the equivalent function as part of the managed node. The concept is identical: a node-local rewrite from the virtual IP to a pod IP.

### To the internet, and in from outside

**[02:25]** Egress: SNAT, then the NAT gateway. [LIVE] The internet saw the NAT gateway's IP.

> *On screen:* An egress packet's source changes from the pod IP to a VPC address on the node, follows the 0.0.0.0/0 route to the NAT gateway, and reaches the internet with the NAT gateway's public IP.

For destinations outside the VPC, the source address is rewritten twice. First the node SNATs the pod IP to a VPC address [BG] (on a standard CNI the node's primary IP, controlled by `AWS_VPC_K8S_CNI_EXTERNALSNAT=false` by default; Auto Mode exposes this as `snatPolicy`). Then the private subnet's route `0.0.0.0/0 → NAT gateway` sends it out, and the NAT gateway translates to its public IP. [LIVE] `wget https://checkip.amazonaws.com` from the pod returned exactly the NAT gateway's public address. Pods in public subnets do not get public IPs automatically [BG].

**[02:31]** From outside: ip targets reach the pod IP directly; instance mode adds a node hop.

> *On screen:* Two inbound arrows from an ALB/NLB are drawn: a solid one straight to the pod IP (ip target), and a dotted one through a node port and an extra hop (instance target).

Because pod IPs are real VPC IPs, the AWS Load Balancer Controller can register them directly as targets (`target-type: ip`), so traffic goes load balancer → pod with no extra hop. With `target-type: instance` the load balancer sends to a NodePort on a node, and kube-proxy (or its equivalent) forwards to a pod, possibly on another node. The live load-balancer experiments for this are in the Exposing Applications video (`concepts/aws-load-balancer-controller/`, `concepts/ingress/`).

### Key takeaways  `[02:37]`

- Same node: host routes via the veth, never leaves the node
- Other node: VPC routing between ENIs, no NAT, no tunnel
- Services are virtual IPs rewritten (DNAT) on the node
- Internet egress is SNAT plus the NAT gateway

---

## Chapter 3 — Network Policies

**Starts at 02:52** · length 01:19 · source `N03-network-policies` · hook: *"A firewall keyed on labels. But is it actually enforced?"*

**What you'll learn.** This chapter follows `concepts/networking/03-network-policies.md`: the rules of Kubernetes NetworkPolicy, the workshop's retail-store lab [W, not executed], the "both ends must agree" decision path, and a live test on the Auto Mode cluster [LIVE] in which policies were accepted but **not enforced**. The cause of that was never determined, and the chapter says so.

### Default: everything can reach everything

**[02:59]** No policy: every pod may talk to every pod and to the internet.

> *On screen:* Pods in several namespaces appear with arrows between all of them and out to the internet, showing that everything is open by default.

[W] Without any policy, every pod may talk to every other pod and to the internet. A NetworkPolicy is a firewall rule keyed on labels rather than IP addresses, so it keeps working as pods come and go. Policies are enforced by the data plane, not by the API server: on EKS that is the VPC CNI network policy agent, which uses eBPF on each node [W]. In the workshop set-up, `curl http://checkout.checkout/health` from the catalog pod succeeds before any policy exists.

**[03:04]** Default-deny egress in ui blocks everything, even DNS: 'Resolving timed out'.

> *On screen:* A default-deny egress policy is applied to the ui namespace, and every arrow out of ui turns red, including the one to DNS.

[W] The lab's first policy, `default-deny` in namespace `ui`, has `podSelector: {}` (all pods in the namespace) and `policyTypes: [Egress]` with no allow rules. Once a policy selects a pod for a direction, everything not explicitly allowed in that direction is denied. The result is `Resolving timed out` when ui calls catalog: the DNS lookup itself is blocked, because DNS is ordinary egress traffic to port 53. Forgetting to allow DNS is the most common way a new egress policy 'breaks everything'.

**[03:09]** Allow service pods and DNS: catalog works; MySQL and the internet stay blocked.

> *On screen:* An allow rule opens ui's egress to service pods and to kube-system DNS: the catalog arrow turns green, while MySQL and the internet stay red.

[W] The second policy allows ui egress to pods labelled `app.kubernetes.io/component: service` in any namespace, plus everything in `kube-system` for DNS. Now ui reaches catalog, but the catalog MySQL pod (`component: mysql`) and `www.google.com` remain blocked. Policies are additive: the allowed set is the union of all policies that select a pod. Return traffic of an allowed connection is allowed automatically because enforcement is stateful [BG].

**[03:14]** catalog ingress: only namespace ui AND pod ui (one 'from' item). orders is denied.

> *On screen:* An ingress policy on catalog appears with one 'from' item combining namespaceSelector ui and podSelector ui; the ui arrow passes and the orders arrow is denied.

[W] Policy `allow-catalog-ingress-webservice` selects the catalog service pods and allows ingress only from a single `from` entry that contains both `namespaceSelector kubernetes.io/metadata.name=ui` and `podSelector app.kubernetes.io/name=ui`. Two selectors inside one item are ANDed: the source must be a ui pod in the ui namespace. Listing them as two separate items would OR them and let in far more. Requests from orders are therefore denied.

**[03:19]** Trap: a podSelector alone means 'in my namespace'. Add a namespaceSelector to fix it.

> *On screen:* A policy with podSelector ui and no namespaceSelector is shown on the orders namespace; it matches nothing, the ui arrow is denied, and the fix adds a namespaceSelector.

[W] The debugging lab applies a policy to `orders` that allows `podSelector: ui` without a namespace selector, and ui is still denied. A `podSelector` on its own means 'pods with this label in the policy's own namespace', so it looks for ui pods inside `orders`, where there are none. Adding `namespaceSelector` fixes it. The DENY is visible in `/var/log/aws-routed-eni/network-policy-agent.log` on the node, with lines showing source IP, destination IP and port, and `Verdict: DENY`.

### Both ends must agree

**[03:29]** Once selected, unlisted traffic is denied: A's egress AND B's ingress must allow.

> *On screen:* A packet from pod A to pod B passes two gates: A's egress check on A's node and B's ingress check on B's node; it is dropped if either gate says no.

Once a pod is selected for a direction, any traffic not listed is denied, so a connection needs two approvals: the egress rule on the sender (if an egress policy selects it) and the ingress rule on the receiver (if an ingress policy selects it). The drop happens on the sender's node for egress and on the receiver's node for ingress. When designing policies, check both ends, and remember that a pod with no policy selecting it in a direction is open in that direction.

### Live test: accepted, but not enforced

**[03:37]** [LIVE] Policies were created fine, yet client and intruder reached web at every step.

> *On screen:* A step table fills in for the live test: with no policy, then default-deny ingress, then an allow-client rule, both client and intruder show 'reached' at every step.

[LIVE] In namespace `net-lab` the test used `web` (port 8080), `client` and `intruder` pods. Step 1 applied `default-deny-ingress` selecting `app=web` with no allow rules; step 2 added `allow-client-to-web` from `app=client` on TCP 8080. Both policies were created without errors, yet client and intruder kept reaching web at both steps and still did about 35 seconds later. Kubernetes accepting a policy object does not mean anything is enforcing it.

**[03:43]** A working enforcer would have blocked both at step 1, and only the intruder at step 2.

> *On screen:* Beside the live results, a second column shows what a working enforcer would give: both blocked at step 1, only the intruder blocked at step 2.

With a working enforcer, step 1 should have made both requests time out, because the policy selects web for ingress and allows nothing. Step 2 should have restored only the client, since its allow rule matches `app=client` on port 8080, while the intruder stayed blocked. Comparing the expected and observed tables is the clearest way to see that the policies were not active. This is why every policy test needs a pod that should be denied, not only one that should be allowed.

**[03:48]** Evidence: no PolicyEndpoints, and the node says DefaultAllow. Cause not determined.

> *On screen:* Two evidence cards appear: 'kubectl get policyendpoints: No resources found' and the node's CNINode showing networkPolicy: DefaultAllow.

[LIVE] The network policy controller normally creates a PolicyEndpoints object for each policy, which the node agent turns into eBPF rules, but `kubectl get policyendpoints` returned 'No resources found' in every namespace. Each node's CNINode showed `networkPolicy: DefaultAllow` and `networkPolicyEventLogs: Disabled`, and the NodeClass had the same settings. The source lists hypotheses (the controller path not active on this cluster or version, a missing setting, interaction with other platform tooling) but verified none, and made no cluster changes to test them.

**[03:52]** Not proof Auto Mode never enforces. The rule: always test a policy with a deny case.

> *On screen:* A caution banner appears: 'not proof Auto Mode never enforces', followed by the rule 'always test with a deny case'.

This finding is specific to one cluster on one day: it does not show that EKS Auto Mode cannot enforce network policies. The practical lesson [BG] is to verify enforcement every time: start with default-deny ingress per namespace, allow DNS in egress, combine namespace and pod selectors, and probe with a throwaway 'intruder' pod that must be blocked. Turning on policy event logs gives you DENY lines to confirm the agent is working.

### Key takeaways  `[03:58]`

- Policies select pods by label; selected = default deny
- Egress default-deny blocks DNS too: allow port 53
- A podSelector alone means the policy's own namespace
- Always prove a policy with a deny test

---

## Chapter 4 — Security Groups for Pods

**Starts at 04:12** · length 01:09 · source `N04-security-groups-for-pods` · hook: *"How do you let only the catalog pods reach the database?"*

**What you'll learn.** This chapter follows `concepts/networking/04-security-groups-for-pods.md`. It is **documented only**: the lab needs RDS and a standard VPC CNI with `ENABLE_POD_ENI=true`, so it was not executed. On the Auto Mode cluster the source only confirmed that the `securitygrouppolicies.vpcresources.k8s.aws` CRD exists [LIVE]; the mechanism and lab flow are [W], and the limits are [BG].

### The problem: shared security groups

**[04:18]** Every pod on a node shares the node's security groups. RDS can't tell catalog from ui.

> *On screen:* Three pods (catalog, ui, orders) sit on one node that carries a single node security group, with an RDS database outside that cannot tell them apart.

[W] By default every ENI on an instance carries the same security groups, so every pod on a node shares the node's SGs. In the workshop, the catalog service is moved from an in-cluster MySQL pod (`catalog-mysql-0`) to an RDS database. The RDS security group can only filter by source security group or CIDR, and from its point of view catalog, ui and orders on that node all look identical.

**[04:24]** To let catalog in you would have to allow the whole node, and then every pod on it.

> *On screen:* The RDS security group opens to the whole node SG, and access arrows appear from every pod on the node, not just catalog.

To let catalog reach RDS with only node-level SGs, you would have to allow the node's security group, and then every pod scheduled on that node could connect to the database. That breaks least privilege and changes whenever pods move between nodes. Security groups for pods solves this by giving selected pods their own ENI and their own security group.

### The fix: a branch ENI per selected pod

**[04:33]** Turn on pod ENIs, then a SecurityGroupPolicy selects pods by label or service account.

> *On screen:* An ENABLE_POD_ENI=true switch flips on the VPC CNI, and a SecurityGroupPolicy card selecting app=catalog with the catalog SG is applied.

[W] Setting `ENABLE_POD_ENI=true` on the VPC CNI lets the VPC Resource Controller, which runs in the EKS-managed control plane, attach a trunk ENI (`aws-k8s-trunk-eni`) to eligible nodes. You then create a `SecurityGroupPolicy` (CRD `securitygrouppolicies.vpcresources.k8s.aws`) that selects pods by label or service account and lists security group IDs. In the lab the SG `<cluster>-catalog` allows TCP 8080 from the VPC CIDR and all egress.

**[04:39]** The controller adds a branch ENI on the trunk, with the catalog SG and its own IP.

> *On screen:* A branch ENI hangs off the node's trunk ENI, carrying the catalog SG and its own IP, and the catalog pod is wired to it.

[W] When a matching pod is created, the VPC Resource Controller sees the match (event `SecurityGroupRequested`), creates a branch ENI (`aws-k8s-branch-eni`) with the listed SGs, and attaches it to the trunk ENI. It annotates the pod with `vpc.amazonaws.com/pod-eni`, showing the branch ENI's private IP, VLAN ID and subnet, and the CNI wires the pod to it on its own VLAN. The pod's traffic is now filtered by its own security group instead of the node's.

**[04:46]** Now RDS allows MySQL from the catalog SG only: catalog gets in, ui and orders don't.

> *On screen:* The RDS rule changes to allow MySQL from the catalog SG only; catalog's arrow turns green while ui and orders turn red.

[W] The RDS security group allows MySQL only from the catalog security group, so the database admits the catalog pod's branch ENI and nothing else on the node. The catalog ConfigMap is pointed at the RDS endpoint (read with `aws rds describe-db-instances`, password from SSM Parameter Store) and catalog is restarted to pick up the new pod ENI. This is least-privilege network access to an AWS service at the pod level.

### Costs, and how it differs from NetworkPolicy

**[04:54]** Limits: Nitro only, capped branch ENIs, slower start, pods must be recreated. [BG]

> *On screen:* A limits panel lists four costs: Nitro instances only, a cap on branch ENIs per instance, slower pod start, and pods must be recreated.

[BG] Trunking works only on certain Nitro instance types, and each instance type allows a limited number of branch ENIs, which caps how many SG-enabled pods a node can run. Pods start more slowly because a branch ENI has to be created and attached. Existing pods do not pick up a new policy: they must be recreated. Plan node sizes and rollouts with these limits in mind.

**[05:00]** Security groups guard pod-to-AWS traffic; network policies segment pod to pod. Use both.

> *On screen:* A two-column comparison appears: security groups for pods (pod to AWS resources, enforced at the ENI) versus NetworkPolicy (pod to pod, enforced by the node agent).

Security groups for pods use security groups and CIDRs, are enforced by the VPC at the ENI, and are best for pod-to-AWS-resource traffic such as RDS or ElastiCache, at the cost of branch-ENI limits. Network policies use pod labels, namespaces and CIDRs, are enforced by the node agent with eBPF, and are best for pod-to-pod segmentation inside the cluster, with no extra ENI cost. EKS recommends using both together [W].

### Key takeaways  `[05:08]`

- Without SGP every pod shares the node's security groups
- SecurityGroupPolicy gives selected pods their own branch ENI
- RDS can then allow exactly the catalog pods
- Costs: Nitro only, ENI limits, slower pod start

---

## Chapter 5 — Custom Networking

**Starts at 05:21** · length 01:07 · source `N05-custom-networking` · hook: *"Node subnet too small? Give pods IPs from another CIDR."*

**What you'll learn.** This chapter follows `concepts/networking/05-custom-networking.md`. It is a workshop lab **not executed here**, because it needs the standard `aws-node` DaemonSet (hidden on Auto Mode) and VPC CIDR changes. The steps and the example result are [W]; the gotchas are [BG]; and the only [LIVE] fact is that the Auto Mode cluster's VPC had a single CIDR and selects subnets with `subnetSelectorTerms`.

### Pods get IPs from a secondary CIDR

**[05:28]** Add a secondary CIDR such as 100.64.0.0/16 (CG-NAT space) with pod subnets in each AZ.

> *On screen:* A VPC box gains a second address block, 100.64.0.0/16, with one pod subnet per Availability Zone drawn inside it.

[W] Custom networking moves pod IPs out of the node's subnet into different subnets, usually carved from a secondary VPC CIDR such as 100.64.0.0/16. That range is CG-NAT space, so it does not clash with typical corporate address plans. In the workshop the VPC has the primary CIDR 10.42.0.0/16 plus 100.64.0.0/16, with 9 subnets: 3 public and 3 private from the primary range and 3 from the secondary range, one per AZ.

**[05:35]** The node keeps its primary ENI; pods sit on secondary ENIs in the 100.64 subnets.

> *On screen:* The node keeps its primary ENI in the 10.42 range, while secondary ENIs in the 100.64 subnets carry the pods.

With custom networking the node's primary ENI stays in the node subnet and keeps the node's own IP, but pods are placed only on secondary ENIs created in the 100.64.x.x subnets. Node and pod address spaces are thus separated, which relieves a small primary subnet. A side effect [BG] is that the primary ENI's IPs are no longer used for pods, so each node loses one ENI's worth of pod capacity.

**[05:40]** One ENIConfig per Availability Zone tells the CNI which subnet and SGs to use.

> *On screen:* Three ENIConfig cards appear, one per Availability Zone, each naming that zone's pod subnet and security groups.

[W] An ENIConfig (`apiVersion: crd.k8s.amazonaws.com/v1alpha1`, `kind: ENIConfig`) tells the CNI which subnet and security groups to use for pod ENIs. You create one per Availability Zone and name each after its AZ, for example `us-west-2a`. Subnets are AZ-scoped, so a node in one AZ must use a pod subnet in that same AZ, which is why one ENIConfig per AZ is needed.

### Configure the CNI, then replace the nodes

**[05:46]** Enable custom networking on aws-node, apply ENIConfigs, select them by zone label.

> *On screen:* Two environment variables are set on the aws-node DaemonSet, the ENIConfigs are applied, and each node is matched to its ENIConfig through its zone label.

[W] The lab runs `kubectl set env daemonset aws-node -n kube-system AWS_VPC_K8S_CNI_CUSTOM_NETWORK_CFG=true`, applies the ENIConfigs, and then sets `ENI_CONFIG_LABEL_DEF=topology.kubernetes.io/zone`. The second variable tells the CNI which node label picks the ENIConfig, so a node in `us-west-2a` uses `ENIConfig/us-west-2a` automatically. Without it you would have to annotate each node by hand.

**[05:51]** Only new nodes use it: create a node group, then pin checkout to it with a nodeSelector.

> *On screen:* A new node group, custom-networking, is created, and the checkout Deployment is patched with a nodeSelector that moves its pod onto it.

[W] Existing nodes keep their old configuration, so the lab creates a new node group (`aws eks create-nodegroup … --nodegroup-name custom-networking --instance-types t3.medium`, min = max = desired = 1, label `type=customnetworking`). It then patches `checkout` with `nodeSelector: eks.amazonaws.com/nodegroup: custom-networking`. Only pods scheduled onto the new nodes receive 100.64.x.x addresses.

**[05:58]** [W] Result: checkout now has 100.64.10.16, while checkout-redis keeps 10.42.12.33.

> *On screen:* Two pod cards compare their addresses: checkout now at 100.64.10.16, checkout-redis still at 10.42.12.33.

[W] In the workshop's sample output the moved `checkout` pod received 100.64.10.16 from the secondary range, while `checkout-redis`, which was not moved, kept 10.42.12.33 from the primary range. The two pods still talk normally inside the VPC, because both ranges are routed locally. Pods in 100.64.x.x are not reachable from outside the VPC without extra routing or NAT [BG], but load balancers with ip targets reach them fine within the VPC.

### Gotchas  [BG]

**[06:05]** You lose one ENI of pod capacity per node, and must replace nodes to use it.

> *On screen:* A gotcha card lists one lost ENI of pod capacity per node and the need to replace nodes before the setting takes effect.

[BG] Because the primary ENI no longer hosts pods, each node loses one ENI's worth of pod IPs, so pod density per node drops slightly. The setting only applies to new nodes, so you must roll every node group to use it. Security groups for pods and network policies work with custom networking, but check the CNI version. Alternatives for IP exhaustion are prefix delegation (denser, same subnet) or an IPv6 cluster.

**[06:10]** The Auto Mode cluster had one CIDR; it picks subnets with subnetSelectorTerms instead.

> *On screen:* The Auto Mode cluster is shown with a single 10.98.0.0/16 CIDR and a NodeClass card using subnetSelectorTerms in place of ENIConfig.

[LIVE] The Auto Mode cluster's VPC had only one CIDR, 10.98.0.0/16, so there was nothing to test custom networking against. Auto Mode does not expose `aws-node` or ENIConfig at all; instead its NodeClass and CNINode carry `subnetSelectorTerms`, here selecting two private subnets, as its own way of choosing node and pod subnets. That equivalence is stated by the source but was not verified with a secondary CIDR.

### Key takeaways  `[06:16]`

- Custom networking puts pod IPs in a secondary CIDR
- ENIConfig per AZ names the pod subnet and SGs
- Turn it on in aws-node, then replace the nodes
- Alternatives: prefix delegation or IPv6

---

## Chapter 6 — Prefix Delegation

**Starts at 06:29** · length 01:13 · source `N06-prefix-delegation` · hook: *"Same ENIs, far more pods: one slot, sixteen IPs."*

**What you'll learn.** This chapter follows `concepts/networking/06-prefix-delegation.md`. The workshop lab was **not executed as written**, because it needs `ENABLE_PREFIX_DELEGATION` on the standard `aws-node` DaemonSet. The concept and lab flow are [W], the m5.large numbers are [BG], and the Auto Mode evidence that prefixes are used by default (`ipAllocationStrategy: PrefixFallback`) is [LIVE].

### One ENI slot: one IP, or a /28 prefix

**[06:37]** Normally an ENI slot holds one IP. With prefix delegation it holds a /28: 16 IPs.

> *On screen:* An ENI with ten slots is shown twice: first each slot holds one IP, then each slot holds a /28 block of 16 addresses.

[W] Normally each ENI slot holds a single secondary IP for one pod. With prefix delegation each slot holds a /28 prefix, a block of 16 contiguous IPs, and ipamd hands pods addresses out of those prefixes. It is switched on with `ENABLE_PREFIX_DELEGATION=true` on the `aws-node` DaemonSet, and needs VPC CNI v1.9.0 or newer [W].

**[06:42]** The ENI count is unchanged, but pod density per node rises a lot.

> *On screen:* The ENI count on the node stays the same while the number of pod slots grows several-fold.

Prefix delegation does not add ENIs: the instance's ENI and slot limits are unchanged. What changes is how many pod IPs each slot carries, so pod density per node rises sharply and fewer ENI attachments and EC2 calls are needed as pods scale. This matters most for small instances, which run out of IPs long before CPU or memory.

### How a new pod gets an IP in prefix mode

**[06:51]** Free IP in a /28, else a new /28, else a new ENI. After that the node is full.

> *On screen:* A decision flow animates: free IP in an existing /28, else request a new /28 on an existing ENI, else attach a new ENI; when all fail, the pod stays Pending.

[W] At node start the CNI assigns one or more prefixes to the primary ENI and keeps a warm pool (`WARM_PREFIX_TARGET`, default 1 spare prefix [BG]). A new pod first gets a free IP from an existing /28. If none is free, the CNI requests another /28 on an existing ENI, and if every ENI is full it attaches a new ENI with its own prefixes. Once the instance's ENI maximum is reached, new pods stay Pending because the node is full.

### The numbers (m5.large)  [BG]

**[07:00]** m5.large: 29 pods without prefixes. /28s could address 432, but EKS caps max pods.

> *On screen:* For an m5.large, two bars compare 29 pods without prefixes against a theoretical 432 addresses with prefixes, with a cap line marking EKS max pods.

[BG] An m5.large has 3 ENIs with 10 slots each. Without prefixes the max-pods formula gives 29; with prefixes the theoretical address count is 3 × 9 × 16 = 432. EKS still caps max pods per node, at 110 for smaller instances and 250 for larger ones, because kubelet and CPU limits make running hundreds of pods on one node impractical. Set `max-pods` deliberately rather than relying on the IP count.

**[07:04]** Each prefix needs a contiguous free /28 block. Fragmented small subnets can fail.

> *On screen:* A subnet map shows scattered used addresses; a request for a contiguous /28 fails in the fragmented area and succeeds in a clean block.

[BG] Each prefix must be a contiguous, aligned block of 16 free addresses in the subnet. In a small or fragmented subnet, where individual IPs are scattered across the range, no free /28 may exist even though plenty of single addresses are free, so prefix allocation fails. Keep a subnet with plenty of free /28 space for prefix mode, or use a fallback strategy like Auto Mode's PrefixFallback.

### Workshop lab, and what Auto Mode showed

**[07:11]** [W] Each node starts with two /28s, for example 10.42.10.192/28 and 10.42.10.80/28.

> *On screen:* A describe-instances query runs and each node returns two /28 prefixes, for example 10.42.10.192/28 and 10.42.10.80/28.

[W] The lab first checks that `aws-node` runs a CNI image of v1.9.0 or newer and that `ENABLE_PREFIX_DELEGATION=true` is set, then queries `aws ec2 describe-instances` filtered by the cluster tag for `NetworkInterfaces[].Ipv4Prefixes[]`. In the workshop's sample output each node showed two /28 prefixes, such as 10.42.10.192/28 and 10.42.10.80/28. Each one is a block of 16 pod addresses ready to use.

**[07:17]** Deploy 150 pause pods and query the instances again: more /28 prefixes appear.

> *On screen:* A Deployment of 150 pause pods is created, and repeating the query shows more /28 prefixes appearing on the nodes.

[W] To consume addresses the lab deploys `pause-pods-prefix` in namespace `other` with 150 replicas of `registry.k8s.io/pause`, waits up to 60 s for it to become available, and repeats the describe-instances query. More /28 prefixes now appear on the nodes, because the CNI requested new prefixes as the existing ones filled. The pause image is used because it does nothing and costs almost no CPU or memory, so only IP capacity is being tested.

**[07:22]** [LIVE] Auto Mode's CNINode says PrefixFallback: prefixes first, single IPs as fallback.

> *On screen:* The Auto Mode CNINode card highlights ipAllocationStrategy: PrefixFallback, ipv4PrefixSize: Auto and 15 addresses per interface.

[LIVE] Each Auto Mode node's CNINode object showed `ipAllocationStrategy: PrefixFallback`, `ipv4PrefixSize: Auto` and `ipv4AddressesPerInterface: 15`. The source reads this as Auto Mode using /28 prefixes by default and falling back to individual IPs when a contiguous /28 is not available; that interpretation was not verified on the cluster. On a standard cluster you would tune `WARM_PREFIX_TARGET`, `WARM_IP_TARGET` and `MINIMUM_IP_TARGET` yourself [BG].

### Key takeaways  `[07:27]`

- Prefix mode puts a /28 (16 IPs) in every ENI slot
- Order: free IP → new /28 → new ENI → node full
- m5.large: 29 pods → up to the EKS max-pods cap
- Keep contiguous free /28 space in your subnets

---

## Chapter 7 — EKS Hybrid Nodes

**Starts at 07:43** · length 01:04 · source `N07-hybrid-nodes` · hook: *"Control plane in AWS, worker nodes on-premises."*

**What you'll learn.** This chapter follows `concepts/networking/07-hybrid-nodes.md`. It is **documented only**: the lab needs a Transit Gateway and a simulated remote network, and the workshop labels the module Preview and warns that running hybrid nodes on EC2 is for the lab only [W]. The concept and lab flow are [W]; the networking requirements are [BG].

### One cluster, two places

**[07:50]** Hybrid nodes run on-premises or at the edge; the control plane stays in the Region.

> *On screen:* An AWS Region box with the EKS control plane and EC2 nodes appears beside an on-premises box holding a hybrid node, linked across the gap.

[W] EKS Hybrid Nodes let you run Kubernetes worker nodes on-premises or at the edge while the control plane stays in an AWS Region. The same cluster schedules pods onto both EC2 nodes and the remote machines. Hybrid nodes are billed per vCPU-hour of attached capacity [W]. In the lab the remote network is simulated and connected through a Transit Gateway.

**[07:55]** Needs private connectivity, non-overlapping routable CIDRs, and Cilium or Calico as CNI.

> *On screen:* Three requirement cards appear on the link: private connectivity (VPN or Direct Connect), non-overlapping routable CIDRs, and Cilium or Calico as the CNI.

[BG] Hybrid nodes need private connectivity between the remote network and the VPC, such as Site-to-Site VPN, Direct Connect or a Transit Gateway. The remote node and pod CIDRs must not overlap with the VPC and must be routable in both directions, because the control plane has to reach kubelets and pods. The VPC CNI cannot run outside AWS, so hybrid nodes use Cilium or Calico instead.

### Connecting a hybrid node

**[08:03]** Create an SSM activation, write a NodeConfig, then nodeadm install and nodeadm init.

> *On screen:* Three command chips run in order: create an SSM hybrid activation, write a NodeConfig file, then run nodeadm install and nodeadm init.

[W] Hybrid nodes authenticate with temporary IAM credentials, provided either by an SSM hybrid activation or by IAM Roles Anywhere. The lab runs `aws ssm create-activation` with a hybrid IAM role, writes a NodeConfig file containing the cluster name and the activation code and ID, then uses `nodeadm install` to install the Kubernetes components and `nodeadm init` to join the cluster. `nodeadm` is the node agent EKS provides for this.

**[08:07]** The node registers with an mi- prefix: an SSM managed instance.

> *On screen:* The new node appears in the node list with a name starting mi-, labelled as an SSM managed instance.

[W] A node registered through SSM shows up in `kubectl get nodes` with an `mi-` prefix, because it is an SSM managed instance rather than an EC2 instance (EC2 nodes use `i-` IDs or IP-based names). This makes hybrid nodes easy to tell apart, and they carry the label `eks.amazonaws.com/compute-type: hybrid` used for scheduling.

### Routing traffic, then cloud bursting

**[08:14]** nginx (3 replicas) prefers compute-type hybrid nodes; an ALB sends traffic there.

> *On screen:* An nginx Deployment with 3 replicas is placed onto the hybrid node through preferred node affinity, and an ALB routes traffic to those pods.

[W] The routing lab deploys `nginx` with 3 replicas in namespace `nginx-remote`, with preferred node affinity for `eks.amazonaws.com/compute-type: hybrid`, and exposes it through an Ingress backed by an ALB. Requests through the ALB are served by the pods on the hybrid node. Pods on a hybrid node can be load-balancer targets only because the remote pod CIDR is routable from the VPC.

**[08:19]** 'Preferred' affinity lets extra replicas burst to EC2 when the hybrid node is full.

> *On screen:* The Deployment scales up; the hybrid node fills, and extra nginx replicas spill over onto EC2 nodes in the Region.

[W] Because the affinity is `preferredDuringSchedulingIgnoredDuringExecution` rather than required, the scheduler places pods on the hybrid node until it is full and then puts the extra replicas on EC2 nodes. This is cloud bursting: on-premises capacity is used first, and the cloud absorbs peaks. A `required` rule would leave the extra pods Pending instead.

**[08:25]** On scale-down, a Kyverno deletion-cost keeps the hybrid pods and removes EC2 pods first.

> *On screen:* On scale-down, the EC2 pods are removed first and the hybrid pods stay, driven by a Kyverno policy setting pod deletion cost.

[W] When a Deployment scales down, Kubernetes may otherwise remove the pods on the hybrid node first (for example, older pods), which would undo the 'on-prem first' intent. The lab uses Kyverno to set a pod deletion cost, the `controller.kubernetes.io/pod-deletion-cost` annotation [BG], so hybrid pods are expensive to delete and the EC2 burst pods are removed first. The cluster then shrinks back to its on-premises footprint.

### Key takeaways  `[08:33]`

- Hybrid nodes run on-prem; the control plane stays in AWS
- Private link and non-overlapping, routable CIDRs are required
- SSM activation + nodeadm join the node (mi- name)
- Preferred affinity + deletion cost give cloud bursting

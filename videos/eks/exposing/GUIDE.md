# AWS EKS — Exposing Applications — Guide

Total length: **06:11**

**Video:** [`EKS-Exposing-Applications.mp4`](EKS-Exposing-Applications.mp4), 1920×1080, 30 fps, with chapter markers. In VLC use *Playback → Chapter*.
**Editable drawings:** [`EKS-Exposing-Applications.excalidraw`](EKS-Exposing-Applications.excalidraw). Open it at excalidraw.com with *Menu → Open*; each scene is a named frame.
**Source:** `EKS/AWS_EKS_fundamentals/`. Chapters follow the numbered files in `concepts/aws-load-balancer-controller/`, `concepts/load-balancers-service-type/`, `concepts/ingress/`, `concepts/gateway-api/` and `labs/01-exposing-applications.md`, in order.

**Execution status:** **Executed live** (cluster eks-workshop, K8s 1.33, 3 × m5.large) for the NLB, Ingress/ALB, IngressGroup and Gateway API. **ExternalDNS was documented only.**

### How to use this guide
- Each **[mm:ss]** line is the on-screen caption, with its exact time in this video.
- *On screen* describes the animation; the paragraph under it explains the idea and the kubectl/YAML/AWS pieces involved.
- Tags follow the source notes: **[LIVE]** = measured on a real EKS cluster, **[W]** = stated by the EKS Workshop, **[BG]** = background knowledge (verify before relying on it). Account IDs and IPs are never shown.

## Chapters

| Starts | Chapter | Length | Source video |
|---|---|---|---|
| 00:00 | [Introduction](#introduction) | 00:12 | `00-intro` |
| 00:12 | [Chapter 1 — Controllers & the AWS LB Controller](#chapter-1--controllers--the-aws-lb-controller) | 01:25 | `X01-controller-pattern-lbc` |
| 01:38 | [Chapter 2 — Service type LoadBalancer → NLB](#chapter-2--service-type-loadbalancer--nlb) | 01:27 | `X02-service-loadbalancer-nlb` |
| 03:05 | [Chapter 3 — Ingress → Application Load Balancer](#chapter-3--ingress--application-load-balancer) | 01:32 | `X03-ingress-alb` |
| 04:38 | [Chapter 4 — Gateway API on EKS](#chapter-4--gateway-api-on-eks) | 01:32 | `X04-gateway-api` |

---

## Introduction

**Starts at 00:00** · length 00:12 · source `00-intro` · hook: *"From a Service YAML to a real AWS load balancer"*

**What you'll learn.** This short opener lists the four chapters of the Exposing Applications topic, in the same order as the source folders: `concepts/aws-load-balancer-controller/`, `concepts/load-balancers-service-type/`, `concepts/ingress/` and `concepts/gateway-api/` (lab text: `labs/01-exposing-applications.md`). Almost everything in this topic was executed live on the `eks-workshop` cluster (K8s 1.33); ExternalDNS is the only part that is documented but not run.

### What this video covers

**[00:07]** Timings shown are from a live EKS cluster run; background facts are marked.

> *On screen:* Four numbered orange circles pop in one after another, each with its chapter title typed next to it, then the agenda fades out.

The chapters build on each other: first the controller pattern that every later feature relies on, then the NLB (L4), then the ALB through Ingress (L7), and finally Gateway API as the newer way to describe the same ALB. Numbers on screen are **[LIVE]** measurements from `EXECUTION_SUMMARY.md` (for example NLB hostname after about 5 s, ALB targets healthy after about 1 min 50 s). Anything the author added from general knowledge is tagged **[BG]** in the source and on screen, so verify those before putting them into a spec.


---

## Chapter 1 — Controllers & the AWS LB Controller

**Starts at 00:12** · length 01:25 · source `X01-controller-pattern-lbc` · hook: *"Who actually builds your load balancer?"*

**What you'll learn.** This chapter explains the idea every other chapter depends on: Kubernetes controllers that turn YAML (desired state) into real AWS resources (actual state). It follows `concepts/aws-load-balancer-controller/01-osi-model-l4-vs-l7.md` → `02-kubernetes-controllers-pattern.md` → `03-lbc-anatomy.md` → `04-lbc-in-action.md`, with the cheat-sheet in `05-cheatsheet-and-glossary.md`. All experiments shown (non-HTTP bytes test, pod delete, drift test) were run live **[LIVE]**.

### 1 · L4 vs L7: how deep does it look?

**[00:18]** An NLB works at L4: it forwards connections and never reads the HTTP inside.

> *On screen:* A client box sends an arrow to an orange NLB box labelled "sees: IP + port", which forwards it unopened to a pod.

OSI layer 4 is the transport layer: TCP/UDP connections, addresses and ports. A Network Load Balancer picks a target and passes the bytes through without parsing them, which is why it is fast and protocol-agnostic. The price is that it cannot make decisions based on HTTP paths, hosts or headers. In EKS, a `Service` of `type: LoadBalancer` handled by the AWS Load Balancer Controller becomes an NLB.

**[00:23]** An ALB works at L7: it reads the request, so it can route by path or host.

> *On screen:* Below the NLB lane an ALB lane draws in: the ALB box reads the request and splits it with a green arrow to `/catalog → catalog` and a blue arrow to `/* → ui`.

Layer 7 is the application layer. An Application Load Balancer terminates the HTTP connection, reads the request line and headers, and then chooses a target group by rules such as path or host. That is what lets one ALB serve many Services, add `X-Forwarded-For` headers, and answer some requests itself. In EKS an `Ingress` with class `alb` (or a Gateway API `Gateway`) becomes an ALB.

**[00:28]** Proof from the cluster: garbage to the ALB got a reply signed by the ALB itself.

> *On screen:* A red-bordered "live test" card appears on the right: non-HTTP bytes via the NLB get a 400 from the app, via the ALB a 400 from the ALB itself (`Server: awselb/2.0`).

**[LIVE]** The author sent bytes that are not valid HTTP to both load balancers. Through the NLB they reached the application, which answered 400 itself, proving the NLB never looked inside. Through the ALB the load balancer rejected them before any pod saw them, and the response carried `Server: awselb/2.0`. That header is a handy debugging clue for the rest of the topic: when you see it, the answer came from the ALB, not from your app.

### 2 · The controller pattern: desired vs current

**[00:34]** You declare what you want. The controller keeps working until AWS matches it.

> *On screen:* A YAML card (`type: LoadBalancer`) flows into a violet API-server box; below it a yellow controller box watches the API server, writes status back, and calls an orange AWS box.

This is the control loop: watch the desired state (`spec`), compare it with the current state, act, then report the result in `status` and events, and repeat. Kubernetes stores your YAML in the API server; it does not create anything in AWS by itself. The AWS Load Balancer Controller is the component that reads that YAML and calls the ELB, EC2 and security-group APIs until AWS matches.

**[00:39]** Kubernetes alone can't build an AWS load balancer. The controller translates.

> *On screen:* The "calls AWS APIs" arrow from the controller to the AWS box (NLB, ALB, target groups, security groups) is the focus while the loop stays on screen.

Built-in Kubernetes controllers (Deployment, ReplicaSet) only create other Kubernetes objects. The source calls the AWS Load Balancer Controller a **direct-control controller**: it also talks to an outside API, so it needs AWS credentials. That is why the controller has an IAM role, and why a missing permission shows up as a failed reconcile in its logs rather than an error from `kubectl apply`.

**[00:43]** Controllers never call each other. They all coordinate through the API server.

> *On screen:* A green "live" card appears: delete one pod → the replacement is created in the same second → the LBC re-registers the new pod IP.

**[LIVE]** Deleting one pod showed three controllers cooperating without ever calling each other: the ReplicaSet controller created a replacement, the scheduler placed it, and the LBC noticed the new pod IP and registered it in the target group. Each one only watched and wrote objects through the API server. This is why you debug by reading objects and events (`kubectl describe`, `kubectl get events`), not by looking for direct calls between components.

### 3 · Anatomy of the AWS Load Balancer Controller

**[00:50]** IRSA: the trust policy pins the exact namespace and ServiceAccount name.

> *On screen:* The controller sits in the centre with five coloured parts around it; the green "ServiceAccount → IAM role (IRSA)" part is the one being described.

IRSA (IAM Roles for Service Accounts) gives the controller pod short-lived AWS credentials through the cluster's OIDC provider. **[LIVE]** The role's trust policy only allows `sub = system:serviceaccount:kube-system:aws-load-balancer-controller-sa` and `aud = sts.amazonaws.com`. So the ServiceAccount name in the Helm values must match exactly: any other pod or ServiceAccount gets AccessDenied. Pod Identity is an alternative to IRSA **[BG]**; the workshop uses IRSA throughout.

**[00:54]** Two replicas run, but only the Lease holder reconciles: high availability.

> *On screen:* The blue "Deployment: 2 replicas, 1 leader (Lease)" part of the anatomy diagram is highlighted.

The Helm chart (3.3.0 here) runs two controller pods, but only one is active at a time. They elect a leader through a `Lease` object, `aws-load-balancer-controller-leader` in `kube-system`; check it with `kubectl -n kube-system get lease aws-load-balancer-controller-leader -o jsonpath='{.spec.holderIdentity}'`. If the leader dies, the other replica takes the lease and continues, so you get high availability without two pods fighting over the same AWS resources. Read the logs of the leader pod when debugging; the standby pod is mostly quiet.

**[00:58]** Finalizers make deletes safe: AWS is cleaned up before the object disappears.

> *On screen:* Attention stays on the anatomy diagram, now including the violet webhooks part (6 mutating + 3 validating) and the pink TargetGroupBinding CRD.

A finalizer is a marker that blocks deletion until a controller has cleaned up. **[LIVE]** On delete, Kubernetes marked the Service *Terminating*, the controller removed the AWS resources (about 5 s), removed its finalizer, and only then did the object disappear (about 30 s in total). If the controller is down or lacks IAM permissions, the object stays Terminating; check with `kubectl get <obj> -o yaml | grep -A2 finalizers` and the controller logs. The other parts on screen matter too: the webhooks check objects as they are saved, so `kubectl apply` can fail when every LBC pod is down, and `TargetGroupBinding` is the CRD that keeps pod IPs registered in target groups.

### 4 · Live experiment: drift in AWS

**[01:04]** I deleted the /echo rule directly in AWS: four rules became three.

> *On screen:* A white ALB-listener panel lists four rules; the red `2 /echo` rule fades away, leaving three.

**[LIVE]** This is the drift experiment. With an Ingress already reconciled into an ALB, the author deleted the `/echo` listener rule directly in AWS, outside Kubernetes. The Ingress YAML still asked for that rule, so desired and actual state now disagreed. The question was: how quickly does the controller notice?

**[01:08]** Polled every 15 s for 90 s: still 3 rules. The controller stayed silent.

> *On screen:* A timeline arrow draws from 0 s to 90 s and six red "3" boxes pop up along it, one per poll.

**[LIVE]** The author polled the rule count every 15 s for 90 s and saw 3, 3, 3, 3, 3, 3: the missing rule stayed missing. The controller did not repair it because nothing in Kubernetes changed. It does not continuously poll AWS for differences. So a hand edit in the AWS console can quietly linger, which matters for anyone who "just quickly fixes" a load balancer by hand.

**[01:12]** Then I touched the Ingress. Two seconds later the rule was back.

> *On screen:* A violet `kubectl annotate ingress echo touched=…` card draws an arrow to the timeline, a green "4" box appears, and the `/echo` rule reappears green in the ALB panel.

Changing anything on the Ingress (here a throwaway annotation, `kubectl annotate ingress <name> touched=$(date +%s) --overwrite`) creates a Kubernetes event. The controller then reconciled, compared the whole picture with AWS, and recreated the rule. **[LIVE]** It took about 2 s. This annotate trick is a safe way to force a reconcile when you suspect drift.

**[01:16]** Event-driven: an edit in AWS fires no Kubernetes event, so nothing reconciles.

> *On screen:* The drift timeline and the restored rule stay on screen while the caption explains why.

The source describes the controller as **event-driven and level-triggered**. Event-driven: it wakes up when a watched Kubernetes object changes, not on a timer against AWS. Level-triggered: once awake it re-reads the full desired and current state instead of replaying single events, so even missed events heal on the next pass. An edit made only in AWS produces no Kubernetes event, so there is nothing to wake the controller until something on the cluster side changes.

**[01:21]** Lesson: never hand-edit controller-managed AWS resources. Change the YAML.

> *On screen:* The full drift experiment (rules panel, polls and fix) remains as the closing picture of the section.

Treat controller-managed load balancers, target groups and their security-group rules as owned by the YAML. If you need a change, edit the Ingress, Service or Gateway and let the controller apply it. Hand edits are either silently kept (until the next reconcile overwrites them) or silently missing, as here. For audits, compare AWS with the YAML using `aws elbv2 describe-rules --listener-arn <arn>` rather than trusting the console view.

### Key takeaways  `[01:25]`

- NLB = L4 connections; ALB = L7 HTTP routing
- Controllers loop: desired (YAML) → actual (AWS)
- LBC: IRSA identity, webhooks, TargetGroupBinding
- Drift in AWS waits for a Kubernetes event

---

## Chapter 2 — Service type LoadBalancer → NLB

**Starts at 01:38** · length 01:27 · source `X02-service-loadbalancer-nlb` · hook: *"One Service, one Network Load Balancer: what really happens?"*

**What you'll learn.** This chapter shows what a `Service` of `type: LoadBalancer` really builds on EKS: a Network Load Balancer created by the AWS Load Balancer Controller. It follows `concepts/load-balancers-service-type/01-introduction-service-types.md` → `02-creating-the-load-balancer.md` → `03-instance-vs-ip-mode.md`, with `04-cheatsheet-and-selftest.md`. Every result shown, including the Classic Load Balancer mistake and the four client-IP experiments, was executed live **[LIVE]**. Watch chapter 1 first for the controller pattern.

### 1 · The Service ladder

**[01:44]** Each step contains the previous one: a LoadBalancer also has a NodePort and a ClusterIP.

> *On screen:* Three nested boxes build up: an orange LoadBalancer box, a yellow NodePort box inside it, and a blue ClusterIP box at the centre.

Service types form a ladder. `ClusterIP` gives a stable virtual IP and DNS name reachable only inside the cluster. `NodePort` adds the same port opened on every node. `LoadBalancer` adds a real cloud load balancer in front of those node ports. So a LoadBalancer Service always also has a NodePort and a ClusterIP; you can see the allocated node port with `kubectl get svc -n <ns> -o wide`.

**[01:49]** In the retail store every Service was ClusterIP. Only the ui needs to be public.

> *On screen:* The nested ladder stays on screen while the caption relates it to the retail store sample app.

In the workshop's retail store, every Service (catalog, carts, checkout, orders and the rest) is `ClusterIP`, because they only talk to each other inside the cluster. Only the `ui` is meant for users, so it is the one the lab exposes. Exposing just the front end keeps the internal services off the internet; the source repeats this as a design rule.

### 2 · Creating the load balancer

**[01:58]** Four annotations on one Service tell the controller exactly what to build.

> *On screen:* A white YAML card fills line by line with four annotations, each paired with a blue meaning (controller, public, register nodes, who may connect).

The four annotations are `service.beta.kubernetes.io/aws-load-balancer-type: external` (hand this Service to the AWS Load Balancer Controller), `aws-load-balancer-scheme: internet-facing` (or `internal`), `aws-load-balancer-nlb-target-type: instance` (or `ip`), and `load-balancer-source-ranges: <your IP>/32`. The source range becomes the NLB security group's allow list, so only your address can connect. The source's minimal correct manifest puts all of them in one file together with `spec.type: LoadBalancer`.

**[02:02]** The DNS name appeared after about 5 s, but targets were healthy only after about 100 s.

> *On screen:* A timeline draws: a dot at t+0 s (kubectl apply), a blue dot at t+5 s (hostname in status), a yellow "NLB provisioning · targets initial" band, and a green dot at t+~100 s (targets healthy).

**[LIVE]** The DNS name of the NLB was written into the Service status (EXTERNAL-IP column) about 5 s after the apply. The load balancer itself, and especially its health checks, take much longer. Targets start in `initial` (`Elb.RegistrationInProgress`) and only became `healthy` after about 100 s. You can follow the state with `aws elbv2 describe-target-health --target-group-arn <arn>`.

**[02:07]** A resolving name is not a working site: poll with retries.

> *On screen:* The provisioning timeline stays visible, emphasising the long gap between the 5 s and 100 s marks.

Scripts and CI checks that stop as soon as `EXTERNAL-IP` is filled will get timeouts or connection errors for the next minute or two. The workshop polls with retries (`curl --retry`) instead of testing once. The same lesson comes back for the ALB in chapter 3: the address is not a readiness signal.

### 3 · The Classic Load Balancer trap

**[02:12]** Built in two commands: the annotate failed, the patch ran without annotations.

> *On screen:* Two command cards appear: a red `kubectl annotate svc … (rejected!)` and a grey `kubectl patch svc … type=LoadBalancer`.

**[LIVE]** This is the mistake kept on purpose in the source. The author tried to annotate the Service first, but that command failed, and the following `kubectl patch` that switched the type to LoadBalancer ran anyway. The result was a LoadBalancer Service with none of the controller annotations. Splitting one change into several imperative commands makes this kind of partial state easy to create.

**[02:16]** Without type: external the legacy code built a Classic LB, open to the whole internet.

> *On screen:* Arrows draw from the commands to a grey "legacy service-controller" box and on to a red "Classic LB · SG tcp 80 from 0.0.0.0/0" box.

Without `aws-load-balancer-type: external`, the AWS Load Balancer Controller ignores the Service and the older in-tree cloud provider code (the `service-controller`) handles it. **[LIVE]** That legacy path built a Classic Load Balancer whose security group allowed TCP 80 from 0.0.0.0/0, open to the whole internet, and no source range applied. You can tell who handled a Service from its events in `kubectl describe svc`: source `service` is the LB Controller, `service-controller` is the legacy code.

**[02:21]** It lived about a minute before I deleted it. Always audit the LB security group.

> *On screen:* A green fix card appears: put the type and annotations in one manifest and `kubectl apply` it; check the event source.

**[LIVE]** The accidental Classic LB existed for about a minute before the author deleted it. The fix is to declare everything in one manifest and apply it, so the controller never sees a half-configured Service. Afterwards, `aws elb describe-load-balancers` (the legacy Classic API) should return nothing, and the load balancer's security group should only allow your intended ranges (`aws ec2 describe-security-groups --group-ids <lb-sg>`).

### 4 · Instance mode vs IP mode

**[02:30]** Instance mode registers nodes. kube-proxy may forward to another node: an extra hop.

> *On screen:* A client → NLB → three nodes diagram draws; a red packet travels from the NLB to node 1's kube-proxy and then along a dashed arrow to the pod on node 3.

In instance mode, the target group contains the worker nodes on the Service's NodePort, not the pods. The NLB sends the connection to any node, and kube-proxy forwards it to a pod, which may live on another node. **[LIVE]** With the default `externalTrafficPolicy: Cluster`, all three nodes were healthy targets even though only one had the pod. Requests arrived at the pod from the two other nodes' IPs, an extra hop plus source NAT. That hop is why instance mode can spread load unevenly and hide the client address.

**[02:34]** IP mode registers pod IPs directly: NLB → pod, no kube-proxy hop. Required for Fargate.

> *On screen:* The instance-mode arrows fade, "IP mode" appears, and a thick green arrow carries the packet straight from the NLB to the pod.

In IP mode (`aws-load-balancer-nlb-target-type: ip`) the target group lists pod IPs on the pod port, so the NLB connects straight to the pod with no node hop. This only works because the VPC CNI gives every pod a real, routable VPC address (see the Networking video). Fargate has no nodes you can register, so Fargate pods require IP mode. The source's comparison table marks IP mode as the recommended choice today **[W/BG]**.

**[02:39]** One annotation switches modes: new target group, same DNS name, no downtime.

> *On screen:* The packet sits on the pod while the IP-mode path stays on screen.

**[LIVE]** Changing the annotation from `instance` to `ip` made the controller create a new target group, because the target type cannot be edited in place. It kept the same NLB and DNS name, so users saw no outage. The targets changed from 3 node IDs on port 31922 to pod IPs on 8080, and scaling `ui` from 1 to 3 gave one pod target per AZ. New targets still passed through `initial` for about a minute before `healthy`.

### 5 · Does the app see the client's IP?

**[02:47]** All four measured live: NLB preservation and in-cluster SNAT are different things.

> *On screen:* A four-row table fills in: instance + Cluster (red, SNAT hides the IP), instance + Local (green), IP mode default (red, app sees the NLB's address), IP mode + `preserve_client_ip.enabled=true` (green, took ~1 min).

**[LIVE]** The source tested all four combinations. `externalTrafficPolicy: Local` kept the client IP because only nodes with a ready pod pass the new health check (`HTTP :<healthCheckNodePort>/healthz`), so no relay hop is needed. In IP mode the app saw the NLB's own interface address until `target-group-attributes: preserve_client_ip.enabled=true` was set, and that took about a minute to take effect. In instance mode preservation was already `true` by default, yet kube-proxy's SNAT still hid the client: preservation at the NLB and SNAT inside the cluster are separate mechanisms.

### Key takeaways  `[02:53]`

- ClusterIP ⊂ NodePort ⊂ LoadBalancer
- Hostname in ~5 s, healthy targets in ~100 s
- Forget type: external → open Classic LB
- IP mode: NLB → pod; client IP needs a setting

---

## Chapter 3 — Ingress → Application Load Balancer

**Starts at 03:05** · length 01:32 · source `X03-ingress-alb` · hook: *"One ALB, many services: routing by path and host"*

**What you'll learn.** This chapter turns an `Ingress` into an Application Load Balancer: one L7 load balancer that routes HTTP by path and host to several Services. It follows `concepts/ingress/01-introduction-ingress.md` → `02-creating-the-ingress.md` → `03-multiple-ingress-ingressgroup.md` → `04-externaldns.md`, with `05-cheatsheet-and-selftest.md`. Path matching, edge actions, failure behaviour and IngressGroup were all tested live **[LIVE]**; ExternalDNS was documented but not executed because creating its IAM role was blocked in that session.

### 1 · One ALB that fans out by path and host

**[03:11]** An NLB per Service only speaks TCP. One Ingress gives one ALB that routes HTTP.

> *On screen:* An Ingress YAML card flows into a yellow LB Controller box, then into an orange ALB box that fans out with green and blue arrows to `Service catalog` and `Service ui`.

With only Service-type load balancers, each public Service would need its own NLB, and an NLB cannot route by URL. An Ingress describes HTTP rules (here `/catalog → catalog`, `/ → ui`), and the controller turns them into one ALB with a listener on HTTP :80, listener rules and one target group per backend Service. One load balancer for many Services is also cheaper.

**[03:16]** Kubernetes only stores the Ingress. IngressClass alb tells the LB Controller it's its job.

> *On screen:* The Ingress → controller → ALB → Services pipeline stays on screen.

Kubernetes ships the Ingress *API* but no Ingress *implementation*; the object just sits in the API server until some controller claims it. `ingressClassName: alb` points at the `IngressClass` named `alb`, which belongs to the AWS Load Balancer Controller (`kubectl get ingressclass`). Without a matching class, nothing happens, and that is a common reason for an Ingress whose ADDRESS stays empty.

**[03:21]** Live: the address appeared in 2 s, but traffic flowed only after about 1 min 50 s.

> *On screen:* Two timeline cards appear at the bottom: blue "ADDRESS filled after 2 s" and green "targets healthy after ~1 min 50 s (probe every 15 s, 2 passes)".

**[LIVE]** `kubectl get ingress` showed the ALB DNS name in the ADDRESS column 2 s after the apply, with the event `SuccessfullyReconciled`. Requests only reached pods after about 1 min 50 s, once the targets had passed their health checks. As with the NLB, the address is not a readiness signal; poll with retries or check `aws elbv2 describe-target-health`.

### 2 · Path matching: Exact vs Prefix

**[03:31]** Exact means exact. Prefix matches whole path segments: /prefixed does not match /prefix.

> *On screen:* Two path cards appear (`/exact` Exact, `/prefix` Prefix) and five request/response pairs fill in: `/exact` 200, `/exact/x` 404, `/exactly` 404, `/prefix/x/y` 200, `/prefixed` 404.

`pathType: Exact` matches only that exact path. `pathType: Prefix` matches the path plus anything below it, on whole path segments. **[LIVE]** The controller translated `Prefix /x` into two ALB conditions, `/x` and `/x/*`, and `Exact /x` into just `/x`. That is why `/prefix/x/y` matched but `/prefixed` did not: it shares letters but not a path segment. The 404s in red came from the ALB itself, because no rule matched.

**[03:35]** Host rules become ALB host-header conditions. Rules are checked in priority order.

> *On screen:* A violet host-rule bar appears: `a.example.test → echo-a`, `b.example.test → echo-b`, other → ALB 404.

A `host:` field in an Ingress rule becomes an ALB host-header condition. **[LIVE]** The author tested it without DNS by setting the header directly: `curl -H 'Host: a.example.test' http://<alb>/`. Rules are evaluated in priority order, and anything that matches no rule falls through to the default action, a fixed 404. Read the real priorities with `aws elbv2 describe-rules --listener-arn <arn>` rather than guessing.

**[03:39]** A 404 with Server: awselb/2.0 came from the ALB itself; any other 404 came from your app.

> *On screen:* The path and host results stay on screen, with the red 404 boxes standing out.

Every response the ALB generates itself carries `Server: awselb/2.0`, including the default 404 for unmatched requests. If a 404 lacks that header, the request did reach a pod and your application returned it. Checking response headers with `curl -I` is the quickest way to tell a routing problem (ALB 404) from an application problem (app 404).

### 3 · The ALB can answer by itself

**[03:46]** Annotations define edge actions: fixed responses and redirects, with zero pods involved.

> *On screen:* Two yellow action cards appear: `GET /teapot → 418 "I am a teapot"` (fixed-response action, no pod) and `GET /go → 301 Location: /prefix` (redirect action).

**[LIVE]** With `alb.ingress.kubernetes.io/actions.<name>` annotations you can define actions the ALB performs itself, and refer to them from a rule as if they were a backend Service. A fixed-response action returned 418 with a message, and a redirect action returned 301 with a Location header, without any pod involved. Edge actions are useful for maintenance pages, simple redirects or blocking paths; the source tests them with `curl -I` and `curl -L`.

**[03:50]** Zero targets gives 503. But when every target is unhealthy, the ALB sends traffic anyway.

> *On screen:* A red "What users saw when backends failed" title appears with two cards: zero targets → 503 from the ALB, and ALL targets unhealthy (wrong success code) → 200, the ALB fails open.

**[LIVE]** Scaling the Deployment to 0 left the target group empty, and the ALB answered 503 itself. Then the author made every target unhealthy on purpose with `success-codes: "299"` while the app returned 200 (target reason `Target.ResponseCodeMismatch`). The ALB still delivered requests and users got 200. That is fail-open: when every target in a group is unhealthy, the ALB routes to all of them instead of returning errors.

**[03:55]** So unhealthy is not always an outage: alert on target health, not only on HTTP errors.

> *On screen:* The two failure cards remain on screen as the caption draws the monitoring lesson.

Because of fail-open, a broken health check (wrong path or success code) can look perfectly fine from the outside: users still get answers. If you only alert on HTTP 5xx rates you would miss it, and you would also lose the protection health checks are meant to give. Alert on unhealthy target counts as well, and check target state with `aws elbv2 describe-target-health`.

### 4 · IngressGroup: many Ingresses, one ALB

**[04:01]** Two namespaces, one group name, one ALB: the workshop's way to cut cost.

> *On screen:* Two Ingress cards (ns ui `/ → ui`, ns catalog `/catalog → catalog`, both `group.name: retail-app-group`) draw arrows into one orange ALB listing rule 1 `/catalog`, rule 2 `/*`, default 404.

By default every Ingress gets its own ALB. With the annotation `alb.ingress.kubernetes.io/group.name`, Ingresses in different namespaces can share one ALB, and the controller merges their rules. The workshop uses this to give two teams one load balancer, which saves the per-ALB cost. `kubectl get ingress -A` shows the same ADDRESS for every Ingress in the group.

**[04:06]** When two Ingresses claim the same path, the lower group.order wins.

> *On screen:* A white `group.order` card appears: lower = evaluated first.

When several Ingresses in a group define overlapping paths, `alb.ingress.kubernetes.io/group.order` decides whose rule comes first, and the lower number wins. **[LIVE]** The controller renumbers the ALB rule priorities across the whole group whenever it changes; after adding Ingresses, an existing `/exact` rule moved from priority 1 to 2. So don't memorise priorities; read them from AWS when you debug.

**[04:08]** The group reconciles as one unit: one bad Ingress froze every other team's changes.

> *On screen:* A red "blast radius [LIVE]" card appears: one invalid Ingress → FailedBuildModel → updates to ALL others froze → fixed ~16 s after deleting it.

**[LIVE]** The author added an Ingress `bad-instance` with `target-type: instance` pointing at a ClusterIP Service, which is invalid because instance targets need a NodePort or LoadBalancer Service. It got a repeating `FailedBuildModel` event, and the controller's reconcile error named the whole *group*. An edit to a healthy Ingress in the same group then did not apply. About 16 s after deleting the bad Ingress, the pending change appeared. Sharing an ALB means sharing its failures, so keep groups small or within one team.

**[04:13]** Deleting the last Ingress of the group removed the whole ALB in about 2 seconds.

> *On screen:* The group diagram and the blast-radius card remain as the caption gives the deletion timing.

**[LIVE]** The ALB belongs to the group as a whole, so it exists as long as at least one Ingress uses the group name. Deleting the last Ingress of the group removed the entire ALB in about 2 seconds, and with it its DNS name. If other things depend on that DNS name, a group of one is fragile: plan names (for example with ExternalDNS) that don't depend on a particular ALB.

### 5 · ExternalDNS: friendly names (documented, not executed)

**[04:19]** Another direct-control controller: it keeps Route 53 records in sync with Ingress hosts.

> *On screen:* A grey-titled section draws: an Ingress card with `host: ui.retailstore.com` → a yellow ExternalDNS controller (IRSA role) → an orange Route 53 private zone record pointing at the ALB, with a "Not run" note.

ExternalDNS is another direct-control controller: it watches Ingresses and Services and creates matching records in Route 53. **[W]** In the workshop it publishes `ui.retailstore.com` into a private hosted zone `retailstore.com` attached to the cluster VPC, so the name resolves only from inside the VPC. The source documents the exact steps (an IRSA role and Helm with `--domain-filter=retailstore.com`) but marks the lab **not executed**, because creating its IAM role was blocked in that session. The annotation `external-dns.alpha.kubernetes.io/hostname` tells ExternalDNS what to publish, while the Ingress `host:` field tells the ALB what to match.

### Key takeaways  `[04:25]`

- Ingress (class alb) → one ALB with HTTP rules
- Exact is exact; Prefix matches whole segments
- Zero targets 503; all unhealthy fails open
- IngressGroup shares an ALB, and its blast radius

---

## Chapter 4 — Gateway API on EKS

**Starts at 04:38** · length 01:32 · source `X04-gateway-api` · hook: *"Split the load balancer from the routes, then canary by weight"*

**What you'll learn.** This chapter shows Gateway API on EKS: the same ALB as an Ingress, but described by separate, role-owned objects (GatewayClass, Gateway, HTTPRoute). It follows `concepts/gateway-api/01-introduction-and-deploy-the-controller.md` → `02-exposing-the-ui.md` → `03-path-based-routing.md` → `04-canary-deployment.md`, with `05-cheatsheet-and-selftest.md`. Roles, status conditions, allowedRoutes, ReferenceGrant and the weighted canary were executed live **[LIVE]**; HTTPS listeners, GRPCRoute and NLB Gateways were not tested **[BG]**. Watch chapter 3 first.

### 1 · Roles: who owns what

**[04:45]** Ingress mixes the load balancer and the routing. Gateway API splits them into roles.

> *On screen:* Three stacked tiers draw from top to bottom: GatewayClass `aws-alb` (infrastructure provider), Gateway `retail-store-gateway` that creates the ALB (platform team), and HTTPRoutes in each app namespace (app teams).

An Ingress puts load-balancer settings and routing rules into one object owned by one person. Gateway API separates them. The `GatewayClass` names the implementation (`controllerName: gateway.k8s.aws/alb`), the `Gateway` defines the listener (HTTP :80) and therefore the ALB, and each `HTTPRoute` attaches routing rules from its own namespace. Platform teams can own the load balancer while app teams change only their routes. The source compares Ingress and Gateway API on blast radius, canaries and cross-namespace sharing; this split is the root of the differences.

**[04:49]** AWS settings move from string annotations to a typed LoadBalancerConfiguration.

> *On screen:* The three role tiers remain on screen as the caption moves to configuration.

With Ingress, AWS settings live in many string annotations such as `alb.ingress.kubernetes.io/scheme`. With the LB Controller's Gateway support they move into a typed custom resource, `LoadBalancerConfiguration`, referenced from the Gateway via `infrastructure.parametersRef`. **[LIVE]** The working set used `spec: {scheme: internet-facing, sourceRanges: ["<cidr>"]}`. Typed fields are validated by the API server, so typos fail at apply time instead of being silently ignored. Health-check settings similarly go into a `TargetGroupConfiguration`.

### 2 · Deploy the controller: the version trap

**[04:54]** At start-up the controller checks which CRDs exist and switches features on or off.

> *On screen:* Two log cards appear side by side: red chart 3.6.1 ("Disabling ALBGatewayAPI: missing required CRDs [ReferenceGrant]") and green chart 3.3.0 ("starting gateway route reconciler").

**[LIVE]** When the controller starts, it checks which Gateway API CRDs are installed and enables or disables its Gateway features based on that. It does not fail loudly when something is missing: it logs a "Disabling …" line and carries on. That makes the set of installed CRDs, and the CRD versions a chart expects, part of your configuration. Check with `kubectl get crd | grep gateway` and the controller logs.

**[04:59]** Chart 3.6.1 silently disabled ALB Gateway support. Pinning 3.3.0 made it work.

> *On screen:* The two chart cards stay on screen and a command line appears below: `kubectl -n kube-system logs <lbc-pod> | grep Disabling`.

**[LIVE]** With chart 3.6.1 the controller disabled ALB Gateway support because a required CRD (ReferenceGrant) was missing, so Gateways were never programmed. Pinning the chart to 3.3.0, the version the workshop expects, made it work; only the NLB Gateway features stayed off. Chart upgrades can silently remove features, so pin versions in your Helm values and grep the startup log for `Disabling` after every upgrade. The source keeps this in its "things that went wrong" list.

### 3 · Exposing the UI, then reading the report card

**[05:08]** Apply four objects in order. The workshop waits for the Gateway to be Programmed.

> *On screen:* Four object boxes draw left to right with arrows between them: GatewayClass → LoadBalancerConfiguration → Gateway (orange) → HTTPRoute.

The objects depend on each other, so the workshop applies them in this order: the class first, then the configuration the Gateway refers to, then the Gateway itself (which creates the ALB), then the routes that attach to it. It waits with `kubectl wait --for=condition=Programmed gateway/<name> -n <ns> --timeout=600s` before testing. *Programmed* means the controller has actually built the load balancer, not just accepted the object.

**[05:15]** Status conditions say what the controller decided, and why, in plain fields.

> *On screen:* Three status rows fill in: Gateway `Accepted=True · Programmed=True` (green), HTTPRoute `Accepted=True · ResolvedRefs=True` (green), and a route from another namespace `Accepted=False NotAllowedByListeners` (red).

Gateway API reports decisions as standard status conditions, unlike Ingress where you read controller events and logs. For a Gateway you want `Accepted` and `Programmed` true; for each HTTPRoute parent, `Accepted` (allowed to attach) and `ResolvedRefs` (backends found and permitted). The failure reasons are spelled out, for example `NotAllowedByListeners` or `RefNotPermitted`. `kubectl describe gateway` shows them, and the cheat-sheet has a `jq` one-liner that prints every route's conditions.

### 4 · Path routing across namespaces

**[05:21]** Check 1: allowedRoutes decides which namespaces may attach routes to the Gateway.

> *On screen:* A Gateway card (`allowedRoutes: from: Same → All`) appears with a dashed red arrow to a red "route r-c (other namespace)" box.

A listener's `allowedRoutes.namespaces.from` decides which namespaces may attach routes. `Same` (only the Gateway's namespace) is the default, `All` allows every namespace, and `Selector` uses labels **[BG, not tested]**. **[LIVE]** A route in another namespace was rejected with `Accepted=False (NotAllowedByListeners)`. This is the first of two guards that let a platform team share one Gateway safely.

**[05:25]** Patched to All: accepted in 3 s, serving after about 17 s (ALB rule propagation).

> *On screen:* The r-c route box turns green and a card appears: patched to All, Accepted in 3 s, `GET /c → 200` after ~17 s.

**[LIVE]** After patching the listener to `from: All`, the route's status flipped to Accepted within 3 s, but requests to `/c` only returned 200 after about 17 s. The gap is the controller writing the new ALB rule and that rule propagating in AWS. As in earlier chapters, a green status condition means the controller has accepted the change, not that traffic is already flowing.

**[05:30]** Check 2: a backend in another namespace needs a ReferenceGrant from that namespace.

> *On screen:* A red "route r-x → Service in lb-demo-b" box appears with a card: no ReferenceGrant → RefNotPermitted, `GET /x → 500`, grant added → 200 within ~15 s; then the box turns green.

The second guard protects the *backend's* namespace. An HTTPRoute may only point at a Service in another namespace if that namespace has a `ReferenceGrant` allowing it (`from: [{kind: HTTPRoute, namespace: <route-ns>}], to: [{kind: Service}]`). **[LIVE]** Without it the route reported `ResolvedRefs=False (RefNotPermitted)` and the path returned 500; after creating the grant in the backend namespace it returned 200 within about 15 s. Both namespaces have to agree: the Gateway owner admits the route, and the Service owner admits the reference.

### 5 · Canary deployment by weight

**[05:37]** Weights 90/10 sent 37 of 40 requests to v1 and 3 to the canary.

> *On screen:* An ALB rule box `/* weighted forward` sends a thick blue arrow to `ui (default theme)` and a thin orange arrow to `ui-v2 (orange theme)`; a card shows `90 / 10 · default 37 · orange 3`.

An HTTPRoute rule can list several `backendRefs`, each with a `weight`, and the controller turns them into an ALB forward action with weighted target groups (visible as `ForwardConfig.TargetGroups[].Weight` in `aws elbv2 describe-rules`). **[LIVE]** With weights 90/10, 37 of 40 test requests reached v1 and 3 reached the canary. That is a sample of 40, so expect the counts to be close to the weights but not exact.

**[05:41]** 50/50 split them 20 and 20.

> *On screen:* The two arrows animate to equal thickness and a second card appears: `50 / 50 · default 20 · orange 20`.

**[LIVE]** Changing the weights to 50/50 split the 40 requests exactly 20 and 20. The change is a small patch to the route, for example `kubectl patch httproute <name> --type json -p '[{"op":"replace","path":"/spec/rules/0/backendRefs/0/weight","value":50}]'`. Because the weights live in the HTTPRoute, the app team can run its own canary without touching the Gateway.

**[05:43]** 0/100: all 40 went to v2. Rollback is the reverse edit.

> *On screen:* The orange arrow becomes thick and the blue one almost disappears; a third card appears with an orange border: `0 / 100 · default 0 · orange 40`.

**[LIVE]** With 0/100, all 40 requests went to v2, which completes the rollout. Rolling back is the same edit in reverse: set the weights back. Compared with Ingress, where canaries need ALB-specific annotations, weighted backends are a standard Gateway API field. That is one of the comparison points in the source's cheat-sheet.

**[05:47]** A weight change took about 15 s to take full effect. Weight 0 keeps the target group warm.

> *On screen:* The three weight cards and the arrows remain on screen while the caption gives the timing.

**[LIVE]** Each weight change took about 15 s to take full effect, the time for the controller to update the ALB rule and for AWS to apply it. Keeping a backend at weight 0 instead of removing it keeps its target group and registered targets, so shifting traffic back is quick. When you automate a canary, wait before measuring after each step so you don't attribute old traffic to the new weights.

**[05:53]** Stickiness was off, so one user could see both versions on consecutive page loads.

> *On screen:* The canary diagram stays as the final scene before the takeaways.

**[LIVE]** The ALB target group had stickiness disabled (`TargetGroupStickiness: disabled`), so each request was weighted independently. A single user could get the default theme on one page load and the orange theme on the next. If a version change must be consistent per user, enable target-group stickiness **[BG, not tested]**, or route testers by header or query parameter first (the source verified header, query and method matches), then widen with weights.

### Key takeaways  `[05:59]`

- GatewayClass → Gateway (ALB) → HTTPRoutes, by role
- Pin a controller version that enables Gateway
- allowedRoutes and ReferenceGrant guard namespaces
- Weighted backends = canary; ~15 s to apply

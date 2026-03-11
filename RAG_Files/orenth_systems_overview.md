# Orenth Systems — Company Overview & Internal Reference

**Founded:** 2007  
**Headquarters:** Dellen, Morcovia (EU operations in Ghentwald, Austria)  
**Employees:** ~1,340 (as of Q3 2024)  
**Industry:** Industrial sensor hardware and edge analytics software  
**CEO:** Sable Korrigan (since 2019)  
**Ticker:** ORNS (Morcovian Exchange)

---

## What We Do

Orenth Systems designs and manufactures ruggedized sensor arrays for use in high-vibration, high-temperature industrial environments — primarily mining, offshore drilling, and heavy rail. Our flagship product line, the **Duravel Series**, has been deployed in 38 countries.

Our software division, **Orenth Analytics**, produces the **Lithos Platform**: an edge-native analytics suite that processes sensor data locally (on-device) rather than sending raw telemetry to the cloud. This reduces latency, lowers bandwidth costs, and addresses data sovereignty requirements in regulated industries.

---

## Product Lines

### Duravel Hardware Series

| Model | Primary Use | Temp Range | IP Rating | Notes |
|---|---|---|---|---|
| Duravel-4X | General vibration/temp | -40°C to 220°C | IP68 | Entry-level; highest volume |
| Duravel-7G | Gas detection + vibration | -55°C to 300°C | IP69K | Used in petrochemical |
| Duravel-9M | Magnetic anomaly + shock | -40°C to 180°C | IP67 | Designed for rail axle monitoring |
| Duravel-11S | Subsea pressure + temp | -10°C to 150°C | IP68 / 600m | Offshore; requires Lithos Subsea module |

The Duravel-4X accounts for approximately 61% of hardware revenue. The 11S line, while low-volume, carries our highest margin at roughly 58% gross.

### Lithos Platform (Software)

Lithos is licensed per-device, per-year. Tiers:

- **Lithos Core** — data aggregation, basic alerting, CSV export. $180/device/yr.
- **Lithos Pro** — adds anomaly detection (rule-based + ML), REST API, dashboard builder. $420/device/yr.
- **Lithos Enterprise** — adds fleet-wide predictive maintenance models, custom model training, SSO, SLA guarantees. Custom pricing (avg. deal: ~$210K ARR).

As of 2024, Lithos Enterprise accounts for 34% of total company revenue despite representing fewer than 90 active customers.

---

## Key People

**Sable Korrigan, CEO** — Former COO of Varent Industrial (acquired by Siemens in 2016). Known for restructuring Orenth's go-to-market from a hardware-only model to hardware + recurring software. Holds a mechanical engineering degree from Universität Ghentwald and an MBA from INSEAD.

**Drex Palloran, CTO** — Co-founder. Originally built the sensor firmware for the Duravel-1 prototype in a rented machine shop. Holds 14 patents in vibration signal processing. Rarely gives interviews.

**Niamh Calvert, VP of Product** — Joined from the data infrastructure space (previously at Confluent). Leading the push toward Lithos 3.0, which will introduce streaming model inference on lower-end hardware via a new quantized runtime called **Veld**.

**Tomas Skerrit, Head of Sales - EMEA** — Responsible for 44% of revenue. Former Honeywell. Notoriously difficult to reach before 10 AM.

---

## Recent History

- **2007:** Founded by Drex Palloran and early investor Yena Osk. First product: a single-axis vibration logger sold to a copper mine in northern Morcovia.
- **2013:** Duravel-4X launched; first international sale (a rail operator in South Korea).
- **2017:** Lithos Platform v1 released. Initial uptake slow; hardware team skeptical of recurring software model.
- **2019:** Sable Korrigan hired as CEO. Board-driven; Palloran remains CTO but cedes day-to-day operations.
- **2021:** Series D ($88M) led by Indval Capital. Funds used to open Ghentwald engineering office and double Lithos team.
- **2022:** Duravel-11S launched after 4 years of development. First subsea contract: a North Sea platform operator.
- **2023:** Lithos Enterprise crosses $30M ARR milestone.
- **2024 Q2:** Announced partnership with RailCore GmbH for integrated predictive maintenance across 11,000 rail assets across central Europe. Largest single deal in company history.

---

## Competitors

| Company | Strengths | Orenth Weakness vs. Them |
|---|---|---|
| Hexis Instruments | Larger product catalog, established mining relationships | Broader hardware range |
| Sentara Edge | Strong cloud-first analytics, better UI | Lithos UX still criticized |
| Vokra Industrial | Lower price point, strong in SE Asia | Orenth expensive in cost-sensitive markets |
| Siemens (MindSphere) | Brand recognition, enterprise IT integration | Orenth can't match brand trust with non-technical buyers |

Orenth's clearest differentiator is the combination of sensor hardware + on-device analytics from a single vendor with deep domain expertise in harsh environments. Most competitors are either pure-hardware or pure-software.

---

## Open Initiatives (2024–2025)

- **Lithos 3.0 / Veld Runtime:** Target release Q1 2025. Will enable ML inference on Duravel-4X without cloud offload.
- **North America Expansion:** Currently <8% of revenue from NA. Hiring a dedicated NA sales team in Q4 2024.
- **Duravel-12R:** Next-gen rail sensor with integrated GNSS and gyroscopic stability metrics. In prototype phase.
- **ISO 27001 Certification:** Underway for Lithos Enterprise to unlock regulated-industry customers in EU.

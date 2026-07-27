export type IssueKind = "road_surface" | "street_light" | "sidewalk_obstruction"

export type Evidence = {
  id: string
  direction: "supports" | "contradicts"
  title: string
  detail: string
  observedAt: string
}

export type Hypothesis = {
  provider: string
  service: string
  serviceCode: string
  score: number
}

export type Duplicate = {
  caseId: string
  relation: string
  score: number
  status: string
}

export type Resolution = {
  status: "resolved" | "unresolved"
  provider: string
  service: string
  serviceCode: string
  confidence: number
  issueDistribution: Record<IssueKind, number>
  hypotheses: Hypothesis[]
  evidence: Evidence[]
  duplicate: Duplicate | null
  nextAction: string
  counterfactual: string
}

export type ResolutionInput = {
  description: string
  locationId: string
  observationDate: string
  uncertaintyMeters: number
  assetId: string
}

export type SampleCase = ResolutionInput & {
  id: string
  label: string
  coordinate: [number, number]
}

export const sampleCases: SampleCase[] = [
  {
    id: "boundary-pothole",
    label: "Boundary road",
    description: "Deep pothole in the westbound lane beside the Route 17 marker",
    locationId: "harbor-boundary",
    observationDate: "2025-04-18",
    uncertaintyMeters: 9,
    assetId: "R17-W-042",
    coordinate: [13.4034, 52.5208],
  },
  {
    id: "transit-light",
    label: "Transit light",
    description: "Light is out above the steps at the station entrance",
    locationId: "northbank-transit",
    observationDate: "2025-10-03",
    uncertaintyMeters: 14,
    assetId: "TR-ENT-118",
    coordinate: [13.4077, 52.5225],
  },
  {
    id: "active-works",
    label: "Active works",
    description: "Construction barriers block the full sidewalk near the permit board",
    locationId: "harbor-works",
    observationDate: "2025-07-12",
    uncertaintyMeters: 7,
    assetId: "P-2025-184",
    coordinate: [13.3996, 52.5188],
  },
  {
    id: "unknown-utility",
    label: "Unknown utility",
    description: "Loose cable and damaged fixture on a shared utility pole",
    locationId: "northbank-utility",
    observationDate: "2025-10-08",
    uncertaintyMeters: 24,
    assetId: "",
    coordinate: [13.4115, 52.5192],
  },
]

const round = (value: number) => Math.round(value * 100) / 100

export function inferIssueDistribution(description: string): Record<IssueKind, number> {
  const text = description.toLowerCase()
  const raw = {
    road_surface:
      0.15 + (/(pothole|road|lane|asphalt|surface)/.test(text) ? 0.75 : 0),
    street_light:
      0.12 + (/(light|lamp|pole|fixture|cable)/.test(text) ? 0.72 : 0),
    sidewalk_obstruction:
      0.13 + (/(sidewalk|barrier|construction|blocked|permit)/.test(text) ? 0.74 : 0),
  }
  const total = Object.values(raw).reduce((sum, value) => sum + value, 0)
  return {
    road_surface: round(raw.road_surface / total),
    street_light: round(raw.street_light / total),
    sidewalk_obstruction: round(raw.sidewalk_obstruction / total),
  }
}

export function resolveIssue(input: ResolutionInput): Resolution {
  const issueDistribution = inferIssueDistribution(input.description)
  const excessiveUncertainty = input.uncertaintyMeters > 40
  const missingAsset = input.locationId === "northbank-utility" && input.assetId.trim() === ""

  if (input.locationId === "harbor-boundary") {
    const confidence = excessiveUncertainty ? 0.61 : 0.91
    const resolved = confidence >= 0.72
    return {
      status: resolved ? "resolved" : "unresolved",
      provider: resolved ? "Regional Roads Authority" : "Shared boundary responsibility",
      service: resolved ? "State route surface defect" : "Provider not yet supported",
      serviceCode: resolved ? "SR-07" : "UNRESOLVED",
      confidence,
      issueDistribution,
      hypotheses: [
        {
          provider: "Regional Roads Authority",
          service: "State route surface defect",
          serviceCode: "SR-07",
          score: confidence,
        },
        {
          provider: "Harbor City Public Realm",
          service: "Local street repair",
          serviceCode: "HC-ROAD-02",
          score: 0.42,
        },
        {
          provider: "Northbank Streets",
          service: "Road maintenance",
          serviceCode: "NB-RD-11",
          score: 0.24,
        },
      ],
      evidence: [
        {
          id: "asset-owner",
          direction: "supports",
          title: "Route segment ownership",
          detail: "Frozen road inventory assigns segment R17-W-042 to the regional authority",
          observedAt: "valid 2024-01-01 onward",
        },
        {
          id: "service-scope",
          direction: "supports",
          title: "Service boundary",
          detail: "SR-07 accepts surface defects on regional route carriageways",
          observedAt: "snapshot 2025-01-15",
        },
        {
          id: "city-boundary",
          direction: "contradicts",
          title: "Municipal boundary overlap",
          detail: "The pin falls inside Harbor City, which creates a plausible but weaker city hypothesis",
          observedAt: "snapshot 2025-02-02",
        },
      ],
      duplicate: {
        caseId: "FRT-2418",
        relation: "Same segment, distinct defect 18 m east",
        score: 0.63,
        status: "open",
      },
      nextAction: resolved
        ? "No further evidence is needed for the prepared route"
        : "Reduce the pin uncertainty below 40 m or confirm the Route 17 marker",
      counterfactual:
        "A local road inventory record that supersedes the regional segment assignment would switch the decision to Harbor City",
    }
  }

  if (input.locationId === "northbank-transit") {
    const confidence = excessiveUncertainty ? 0.65 : 0.88
    const resolved = confidence >= 0.72
    return {
      status: resolved ? "resolved" : "unresolved",
      provider: resolved ? "Northbank Transit Operations" : "Transit boundary unresolved",
      service: resolved ? "Station entrance lighting" : "Provider not yet supported",
      serviceCode: resolved ? "TR-LIGHT" : "UNRESOLVED",
      confidence,
      issueDistribution,
      hypotheses: [
        {
          provider: "Northbank Transit Operations",
          service: "Station entrance lighting",
          serviceCode: "TR-LIGHT",
          score: confidence,
        },
        {
          provider: "Northbank Streets",
          service: "Public lighting",
          serviceCode: "NB-LGT-01",
          score: 0.51,
        },
        {
          provider: "Private frontage manager",
          service: "No public service code",
          serviceCode: "PRIVATE",
          score: 0.22,
        },
      ],
      evidence: [
        {
          id: "transit-asset",
          direction: "supports",
          title: "Entrance asset register",
          detail: "TR-ENT-118 is operated and maintained by Northbank Transit",
          observedAt: "valid 2023-09-01 onward",
        },
        {
          id: "policy",
          direction: "supports",
          title: "Lighting service definition",
          detail: "TR-LIGHT includes fixtures physically attached to station entrance structures",
          observedAt: "snapshot 2025-09-01",
        },
        {
          id: "sidewalk",
          direction: "contradicts",
          title: "Sidewalk layer",
          detail: "The entrance footprint intersects a city maintained sidewalk",
          observedAt: "snapshot 2025-06-19",
        },
      ],
      duplicate: {
        caseId: "FRT-2094",
        relation: "Same asset and issue class",
        score: 0.92,
        status: "in progress",
      },
      nextAction: resolved
        ? "Review the likely duplicate before preparing another report"
        : "Confirm whether the failed fixture is attached to the entrance canopy",
      counterfactual:
        "A fixture mounted on the freestanding sidewalk pole would switch the route to Northbank Streets",
    }
  }

  if (input.locationId === "harbor-works") {
    const eventDate = new Date(`${input.observationDate}T00:00:00Z`)
    const permitActive =
      eventDate >= new Date("2025-06-01T00:00:00Z") &&
      eventDate <= new Date("2025-08-31T23:59:59Z")
    const confidence = permitActive && !excessiveUncertainty ? 0.84 : 0.64
    const resolved = confidence >= 0.72
    return {
      status: resolved ? "resolved" : "unresolved",
      provider: resolved ? "Harbor City Works Coordination" : "Works responsibility unresolved",
      service: resolved ? "Active permit obstruction" : "Provider not yet supported",
      serviceCode: resolved ? "HC-PERMIT-08" : "UNRESOLVED",
      confidence,
      issueDistribution,
      hypotheses: [
        {
          provider: "Harbor City Works Coordination",
          service: "Active permit obstruction",
          serviceCode: "HC-PERMIT-08",
          score: confidence,
        },
        {
          provider: "Greenline Civil, permit delegate",
          service: "Contractor correction path",
          serviceCode: "DELEGATED",
          score: permitActive ? 0.71 : 0.18,
        },
        {
          provider: "Harbor City Public Realm",
          service: "Sidewalk obstruction",
          serviceCode: "HC-WALK-04",
          score: permitActive ? 0.38 : 0.68,
        },
      ],
      evidence: [
        {
          id: "permit",
          direction: permitActive ? "supports" : "contradicts",
          title: permitActive ? "Permit active at event time" : "Permit outside valid interval",
          detail: "Permit P-2025-184 covers the pinned work area and delegates first response",
          observedAt: "valid 2025-06-01 to 2025-08-31",
        },
        {
          id: "obligation",
          direction: "supports",
          title: "Obligation scope",
          detail: "The frozen permit requires an accessible pedestrian passage during works",
          observedAt: "recorded 2025-05-22",
        },
        {
          id: "base-maintainer",
          direction: "contradicts",
          title: "Base sidewalk maintainer",
          detail: "Public Realm retains normal maintenance outside the permit interval",
          observedAt: "valid 2021-01-01 onward",
        },
      ],
      duplicate: null,
      nextAction: resolved
        ? "The city permit desk remains the accountable public route during the delegation interval"
        : "Check whether the permit was extended or choose the observation date again",
      counterfactual:
        "An observation after the permit expiry without an extension would return responsibility to Public Realm",
    }
  }

  const confidence = missingAsset || excessiveUncertainty ? 0.53 : 0.67
  return {
    status: "unresolved",
    provider: "Unknown utility or attachment owner",
    service: "No supported reporting route",
    serviceCode: "UNRESOLVED",
    confidence,
    issueDistribution,
    hypotheses: [
      {
        provider: "Northbank Streets",
        service: "Public lighting",
        serviceCode: "NB-LGT-01",
        score: 0.55,
      },
      {
        provider: "Unknown utility",
        service: "Attachment fault",
        serviceCode: "UNKNOWN",
        score: 0.53,
      },
      {
        provider: "Private network operator",
        service: "No public service code",
        serviceCode: "PRIVATE",
        score: 0.31,
      },
    ],
    evidence: [
      {
        id: "shared-pole",
        direction: "supports",
        title: "Shared support structure",
        detail: "The pole geometry intersects lighting and utility attachment layers",
        observedAt: "snapshot 2025-09-18",
      },
      {
        id: "missing-id",
        direction: "contradicts",
        title: "No attachment identifier",
        detail: "Public records do not identify the owner from location alone",
        observedAt: "query 2025-10-08",
      },
      {
        id: "security",
        direction: "contradicts",
        title: "Sensitive infrastructure guard",
        detail: "The system will not expose detailed utility topology",
        observedAt: "policy v1.0",
      },
    ],
    duplicate: null,
    nextAction: "Add a close photo of the public asset label, not the cable routing",
    counterfactual:
      "A verified lighting asset label would support Northbank Streets, while a utility attachment identifier would support its registered operator",
  }
}

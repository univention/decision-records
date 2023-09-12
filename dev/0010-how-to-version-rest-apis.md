
# How to version HTTP-based REST APIs

---

- status: draft
- supersedes: -
- superseded by: -
- date: {YYYY-MM-DD when the decision was last updated}
- author: {contact or informed captain for this ADR}
- approval level: medium
- coordinated with: teams maintaining UCS and N4K, software architect, product management
- source: https://git.knut.univention.de/groups/univention/dev/internal/dev-issues/-/epics/15
- related: [ADR 0002 - Versioning of APIs and artifacts](0002-versioning-of-apis-and-artifacts.md), [ADR 0009 - How to change HTTP based REST APIs](0009-how-to-change-rest-apis.md)
- scope: all Univention HTTP/REST APIs
- resubmission: -

---

## Context and Problem Statement

Versioning is a technique to handle changes in APIs.
It includes _communicating_ changes to clients, _deprecation_ markers, grace periods, public documentation, ...

This ADR defines _how_ breaking changes to the schema or behavior of an API should be handled.

[ADR 0009 - How to change HTTP based REST APIs](0009-how-to-change-rest-apis.md)
defines _when_ changes are considered breaking, and this ADR applies, as well as when it doesn't.

A [guideline in the Development Handbook](https://univention.gitpages.knut.univention.de/dev/internal/dev-handbook/guidelines/change-rest-apis.html)
extends ADR 0009 with more variants and examples.

## Decision Drivers

- _Consistency_ with Univention's existing REST APIs.
- _Maintainability_ of the solution in the API server.
- _Maintainability_ of the solution in API clients.
- _Standardization_: Applies public specifications (e.g., RFC) or industry standards.
- _Usability_, in the sense of "less error-prone", "easy to implement", or "intuitive" for API-server authors.
- _Usability_, in the sense of "less error-prone", "easy to implement", or "intuitive" for API-client authors.

## Considered Options

- No versioning
- URI versioning
- Query string versioning
- Query string feature flags
- Header versioning
- Media type versioning

## Pros and Cons of the Options

Evaluate different options for breaking and non-breaking changes.

### No versioning

Changes, breaking and non-breaking, are released without an explicit technical way to communicate it to clients.
It's entirely up to clients to handle the change.

- Good, because breaking _and_ non-breaking it requires minimal changes in the server.
- Good, because non-breaking changes require minimal or no changes in clients.
- Neutral, because for breaking changes and when used for purely internal APIs and when all clients are known,
  the reduced coding effort and complexity in the server
  can balance the increased coordination effort of updating all clients simultaneously.
- Bad, because breaking changes break unchanged clients when they access changed or removed fields.
- Bad, because breaking changes increase the complexity in clients that have to handle unchanged and changed API servers.
- Bad, because it requires coordination of the team maintaining the server with all teams maintaining clients.

### URI versioning

When an API provider wants to introduce a breaking change, they create a new URI for it.
The server continues to serve the old schema and behavior at the old URI.

Client developers are notified about the change
and offered a grace period to update their clients to work with the new version.
The server stops supporting the old version when the deprecation period ends.
Clients who have not switched to the new version by then will break.

The most typical way to implement URI versioning
is by adding a version string (e.g., `v2`) as a prefix to the path component of the URI to be versioned
(e.g., `https://fqdn/myapi/v2/myresource`).

- Good, because _consistent_ with our existing HTTP APIs:
  - [UCS@school ID Connector API](https://docs.software-univention.de/ucsschool-id-connector/admin.html#id12)
  - [ID Broker Self Disclosure API](https://docs.software-univention.de/idbroker-self-disclosure-api-manual/routes.html)
  - [ID Broker Provisioning API](https://git.knut.univention.de/univention/dev/education/ucsschool-api-plugins/id-broker-plugin/-/blob/main/provisioning_plugin/plugin.py#L38)
  - [ID Broker SDDB API](https://git.knut.univention.de/univention/dev/education/id-broker/id-broker-self-disclosure-db-builder/-/blob/main/id-broker-self-disclosure-db-builder/sddb_builder/rest/main.py#L36)
  - [UCS@school import API](https://git.knut.univention.de/univention/dev/education/ucsschool/-/blob/5.2/ucs-school-import/modules/ucsschool/http_api/app/urls.py#L69)
  - [Kelvin API](https://docs.software-univention.de/ucsschool-kelvin-rest-api/resource-schools.html#schools-list-and-search)
  - [Provisioning API](https://docs.software-univention.de/nubus-kubernetes-customization/latest/en/api/provisioning.html#openapi-schema)
  - [SCIM API](https://git.knut.univention.de/univention/dev/projects/scim/scim-services/-/blob/main/scim-server/src/univention/scim/server/config.py#L57)
- Good, because non-breaking changes require minimal or no changes in clients.
- Good, because positive _usability_, in the sense of "less error-prone" through better _visibility_:
  That an API is versioned can't be overlooked, if it's part of the URL.
- Good, because positive _usability_, as it is easy to implement in clients,
  as all libraries and frameworks allow to define the URL,
  but they may not expose a possibility to set e.g. headers.
- Good, because fulfills _standardization_ expectations by the API's audience:
  API-client programmers are used to URI versioned APIs, because it's the de-facto standard.
- Good, because the _maintainability_ of the API-client is well plannable.
  Clients are not immediately affected by version changes.
  Because the old version stays available during the deprecation period,
  they can adapt to the new version at a time of their choosing.
- Neutral, because there is no public specification how to implement this versioning style.
  But there is a default: `v<version>`.
- Neutral, because the _maintainability_ of the API-server is the same when using URI, query, header or media type versioning.
  All of them are part of the request (object) and as such accessible in the server's code to direct the control flow
  (to generate different responses for different versions).
- Bad, because it versions an entire API, instead of versioning only the part that changes.
- Bad, because version strings in URIs complicate the implementation of HATEOAS.
- Bad, because in the REST architectural style, a resource must not be identified by multiple identifier (URI).

### Query string versioning

When a client wants to access a resource with a specific version,
they can specify it by adding a parameter to the query string
(e.g., `https://fqdn/myapi/myresource?version=2`).
When omitted, the parameter should default to a sensible value that does not break older clients (e.g., `1`)
or to what is defined in a published versioning policy.

New versions and deprecations are communicated and handled as described for URI versioning.

- Good, because non-breaking changes require minimal or no changes in clients.
- Good, because only the object whose API changed is versioned.
- Bad, because versions in query strings complicate the implementation of HATEOAS.

### Query string feature flags

The API offers clients to change its behavior using parameters in query strings
(e.g., to change the format of the ID field: `https://fqdn/myapi/myresource?id-format=uuid`).
When omitted, the API applies a backwards-compatible default behavior.

- Good, because for small changes no new version for the whole API (like in URI versioning) is needed.
- Good, because it's backwards-compatible.
- Bad, because it makes schema validation impossible, as the schema changes with individual queries.
- Bad, because it hides breaking changes from the operator and indirect clients.
  E.g., while the direct client is aware of the change (as it explicitly requested it),
  if the data is passed on to a third service, it (and the operator installing it) won't know about it and may break.

### Header versioning

When a client wants to access a resource with a specific version,
they send a custom header with the version
(e.g., `My-API-Version: 2`).
When omitted, the value should default to a sensible value that does not break older clients (e.g., `1`)
or to what is defined in a published versioning policy.

New versions and deprecations are communicated and handled as described for URI versioning.

- Good, because regardless of version an object has the same URI.
- Good, because only the object whose API changed is versioned.
- Bad, because header versioning complicates web server caching.
- Bad, because clients must send a custom header with every request,
  and some libraries and auto-generated clients don't support that.
- Bad, because request headers are usually not logged, impeding debugging and statistics generation.
- Bad, because requiring custom headers complicates the implementation of HATEOAS.
- Bad, because HTTP already defines headers (`Content-Type`)
  listing [MIME types](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/MIME_types)
  to determine the format of content. Those are used in HTTP's content-negotiation mechanism.

### Media type versioning

When a client wants to access a resource with a specific version,
they send an Accept header with a custom value
(e.g., `Accept: application/vnd.univention.v2+json`).
REST API client should never omit the `Accept` header.
The server can decide whether to return an HTTP error or a sensible default value
when clients use the typical `Accept: application/json` instead of the vendor string.

New versions and deprecations are communicated and handled as described for URI versioning.

- Good, because regardless of version an object has the same URI.
- Good, because only the object whose API changed is versioned.
- Good, because it works well with HATEOAS.
- Good, because it allows for the versioning of request or response representations separately.
- Bad, because media type versioning complicates web server caching.
- Bad, because clients must send a custom header value with every request, and some libraries and auto-generated clients don't support that.
- Bad, because request headers are usually not logged, impeding debugging and statistics generation.
- Bad, because it leads to [media type proliferation](https://www.mnot.net/blog/2012/04/17/profiles)

## Decision Outcome

Chosen option: "URI versioning".

The discussion that led to this decision emphasized the need for clear guidance for developers
to change an API version only in cases of unavoidable breaking changes
and to show the various other preferred methods they can use for non-breaking changes.

Global versioning is the coarsest method available,
which is a significant disadvantage compared to the other techniques discussed in the ADR.
We deem global versioning acceptable
if developers try to keep it to a minimum
and strive to use other possibilities to introduce changes.
See the point above regarding guidance.

We ruled out header and media type versioning
due to concerns about compatibility with customers' third-party tools.

Query-string and local-URI versioning are valid alternatives.
However, this could lead to a wild mix of versions within one API,
which would confuse customers and increase support effort.

We agreed that global URI versioning should be used,
given the context outlined above,
as it's easy to understand,
which outweighs the lack of granularity if used infrequently.

### Consequences

URI and query string versioning are cache-friendly;
header versioning and media type versioning are not.
Whether transparent HTTP caching is important depends on the use case.
For REST APIs it often isn't relevant.

Use all available deprecation communication mechanisms to inform API client authors if they are using an old version.

- Set an HTTP header (RFC 9745).
- Set the `deprecated` flag in the OpenAPI specification.

### Risks

<!-- It's OK to repeat points from the above "Cons of the Options". -->
<!-- Maybe use "Risk storming" to identify risks. -->

- When implementing the decision, a {small, medium, high} risk exists, that {…}.
- …

### Confirmation

{Describe how the implementation of/compliance with the ADR is confirmed. E.g., by a review or an ArchUnit test.
 Although we classify this element as optional, it is included in most ADRs.}

## More Information

- [REST Misconceptions Part 6 - Versioning and Hypermedia](https://t-code.pl/blog/2016/03/rest-misconceptions-6/)
- [Versioning RESTful Services](https://web.archive.org/web/20210506225341/http://codebetter.com/howarddierking/2012/11/09/versioning-restful-services/)
- [Bad HTTP API Smells: Version Headers](https://www.mnot.net/blog/2012/07/11/header_versioning)
- [REST is not about APIs, Part 1](https://nirmata.com/2013/10/01/rest-apis-part-1/)
- [There Is No Right Way](https://thereisnorightway.blogspot.com/2011/02/versioning-and-types-in-resthttp-api.html)
- [Implement versioning](https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design#implement-versioning)

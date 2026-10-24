# API Design Evaluation Criteria — With Examples

These criteria evaluate the REST API design principles in the research document. The examples are illustrative: they show what evaluators might encounter, how to recognize a problem, and what actionable feedback could look like. They are not findings about a particular API.

For every finding, identify **the affected endpoint or schema, the observed behavior, the consequence for consumers, the recommended change, and how to verify the improvement**.

Distinguish between a **demonstrated defect**, a **documentation gap**, and **behavior that has not yet been verified**. An OpenAPI specification that declares an `Idempotency-Key` header, for example, does not prove that duplicate execution is prevented. Conversely, an undocumented mechanism may exist in the implementation.

Apply conditional criteria only where relevant. A read-only API does not need write-concurrency protection; an API without webhooks does not need webhook documentation. Perform mutation, security, and load tests in an authorized test environment.

The criteria retain the guide’s recommended conventions. **Standards clarifications** distinguish those recommendations from requirements of the underlying specifications.

---

## 1. Resource-Oriented URI Design

### What to assess

Evaluate whether the API is organized around identifiable domain resources rather than actions or implementation details.

Look for noun-based paths, consistent pluralization, lowercase naming, and kebab-case for multi-word resource names. Nesting should communicate meaningful ownership without producing unnecessarily deep hierarchies. Resources that can be addressed independently should have appropriate direct access paths.

Also check for a clear, explicit versioning strategy, applied consistently across the API. The research permits both path-based and header-based versioning. api_design_theoretical_deeprese…

### Examples

| Pattern to examine | Why it is problematic under this guide | Preferred example |
|---|---|---|
| `GET /getUsers` | The path repeats an action already expressed by the HTTP method. | `GET /v1/users` |
| `POST /createArticle` | Resource creation is expressed as a command rather than an operation on a collection. | `POST /v1/articles` |
| `/users/{id}` alongside `/article/{id}` | Consumers must remember inconsistent singular/plural conventions. | `/users/{id}` and `/articles/{id}` |
| `/OrderItems` | Does not follow the guide’s lowercase, kebab-case convention. | `/order-items` |
| `/users/42/articles/93/comments/17` | Accessing one comment requires carrying an unnecessarily long ancestry. | `/comments/17`, where independent addressing fits the domain. |

A meaningful nested collection is not automatically a problem. For example, `POST /v1/articles/93/comments` clearly communicates which article receives the comment. The guide pairs this with direct access through `/v1/comments/17`. api_design_theoretical_deeprese…

### Feedback should explain

Identify the problematic paths and explain how their structure makes the API harder to predict. Recommend concrete alternatives, not simply “make the API more RESTful.”

**Example feedback:**

> `POST /createArticle` and `GET /getArticles` expose actions as separate paths. Consolidate them under `/v1/articles`, using POST for creation and GET for retrieval. Apply the same plural, lowercase convention to the remaining collections. For existing consumers, document a migration rather than removing the old paths without notice.

**Re-evaluation check:** Inspect the complete route inventory, including less-used endpoints, and confirm that naming, nesting, and versioning follow the adopted conventions.

---

## 2. HTTP Method Semantics

### What to assess

Evaluate whether HTTP methods accurately communicate the requested operation.

`GET` should retrieve information rather than request a business-state change. `POST` should represent creation or appropriate processing operations. `PUT` should represent replacement, `PATCH` partial modification, and `DELETE` removal. Similar operations should use the same method conventions throughout the API.

Pay particular attention to misleading uses of PUT and to whether repeated DELETE requests have an idempotent effect. api_design_theoretical_deeprese…

### Examples

**Problematic:**

```http
GET /v1/users/42?delete=true
```

Suppose this request deletes the user. The operation is a mutation disguised as retrieval.

**Preferred:**

```http
DELETE /v1/users/42
```

Another problem is a `PUT /v1/users/42` endpoint that changes only the fields supplied and preserves every omitted field. That behavior resembles a partial update and should be examined under the PATCH criterion.

For DELETE, this sequence can be acceptable:

```text
First DELETE  /v1/users/42 → 204
Second DELETE /v1/users/42 → 404
```

The user remains deleted after both requests. Different response codes do not, by themselves, mean that DELETE is non-idempotent. api_design_theoretical_deeprese…

**Standards clarification:** GET safety does not prohibit incidental logging. Likewise, POST is not inherently idempotent, but an API may deliberately provide idempotent POST behavior. Evaluate the requested effect, not whether any internal state changes at all. [RFC Editor](https://www.rfc-editor.org/rfc/rfc9110.html)

### Feedback should explain

Explain what the method communicates, what the endpoint actually does, why that mismatch matters, and which method better represents the operation.

**Example feedback:**

> `GET /v1/users/42?delete=true` deletes a user even though GET communicates retrieval. Replace it with DELETE on the user resource, and ensure GET requests cannot trigger account deletion.

**Re-evaluation check:** Exercise each method against disposable test resources and inspect the resulting business state, including repeated requests.

---

## 3. HTTP Status Codes and Response Semantics

### What to assess

Determine whether status codes and headers accurately communicate outcomes.

The expected patterns in this framework include:

| Outcome | Expected response pattern |
|---|---|
| Successful retrieval | `200 OK` with the representation |
| Successful resource creation | `201 Created`, with the new resource’s location |
| Successful operation intentionally returning no representation | `204 No Content` |
| Work accepted but still incomplete | `202 Accepted` |
| Requested resource does not exist | `404 Not Found` |
| Authenticated caller lacks permission | Typically `403 Forbidden` |
| Conditional update uses a stale version | `412 Precondition Failed` |
| Caller exceeds a rate limit | `429 Too Many Requests` |

These patterns appear across the guide’s resource, concurrency, asynchronous-processing, traffic-management, and authorization sections. api_design_theoretical_deeprese… api_design_theoretical_deeprese… api_design_theoretical_deeprese… api_design_theoretical_deeprese…

### Examples

**Problematic:**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"success": false, "error": "Article not found"}
```

The HTTP response reports success while the body reports failure.

**Preferred:**

```http
HTTP/1.1 404 Not Found
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/article-not-found",
  "title": "Article not found",
  "status": 404
}
```

For creation:

```http
HTTP/1.1 201 Created
Location: /v1/articles/93
Content-Type: application/json

{"id": 93, "title": "Designing Better APIs"}
```

**Standards clarification:** A valid `Location` can be relative or absolute. A `204` response must not contain response content. Do not reject a valid relative location merely because the guide’s creation example uses an absolute URI. [RFC Editor](https://www.rfc-editor.org/rfc/rfc9110.html)

### Feedback should explain

Identify responses that obscure whether work succeeded, failed, or remains pending. Explain the client behavior enabled by the corrected status and headers.

**Example feedback:**

> `GET /v1/articles/999` returns 200 for a missing article. Return 404 with the standard error representation so clients can distinguish missing resources from successful retrieval without inspecting a custom `success` flag.

**Re-evaluation check:** Test successful, missing-resource, validation, authorization, and applicable asynchronous outcomes—not just the happy path.

---

## 4. Partial and Full Resource Updates

### What to assess

Evaluate whether update operations have explicit, predictable semantics.

For PUT, determine whether the supplied representation expresses replacement state and whether omitted properties have documented behavior.

For PATCH, determine whether the payload describes changes, whether omitted properties remain unchanged, and whether the patch format is documented. Examine the meaning of `null`, array handling, and retry behavior.

The research recommends JSON Merge Patch for conventional object-oriented CRUD updates and JSON Patch where granular document or array operations are needed. api_design_theoretical_deeprese…

### Examples

Suppose the current editable representation is:

```json
{
  "name": "Riley",
  "email": "old@example.com",
  "nickname": "R",
  "tags": ["editor", "reviewer"]
}
```

This is a clear partial update:

```http
PATCH /v1/users/42
Content-Type: application/merge-patch+json

{"email": "new@example.com"}
```

The intended result changes the email while retaining the other properties.

With JSON Merge Patch:

```json
{"nickname": null}
```

requests removal of `nickname`, while:

```json
{"tags": ["editor"]}
```

replaces the array rather than removing one element through a separate array operation. These behaviors should be explicit in the API documentation. [RFC Editor](https://www.rfc-editor.org/rfc/rfc7396.html)

**Standards clarification:** PUT replacement does not universally mean “assign null to every omitted field.” The API must define its replacement representation, constraints, and treatment of omitted properties. [RFC Editor](https://www.rfc-editor.org/rfc/rfc9110.html)

### Feedback should explain

Describe the exact ambiguity and recommend a complete update contract, including the media type.

**Example feedback:**

> `PATCH /v1/users/{id}` accepts JSON, but its documentation does not explain whether null deletes a property or stores a null value. Adopt and document a specific patch format. Include examples for an omitted property, explicit null, and array replacement, and ensure the implementation follows those examples.

**Re-evaluation check:** Test omission, null, arrays, invalid changes, and repeated application. Do not assume every PATCH operation is idempotent. [RFC Editor](https://www.rfc-editor.org/rfc/rfc5789.html)

---

## 5. Collection Filtering and Sorting

### What to assess

Evaluate whether collections provide flexible, predictable query mechanisms rather than requiring separate endpoints for every query variation.

Check exact-match filtering, a systematic syntax for complex comparisons, consistent parameter names, sorting direction, and multiple sort fields where useful.

The research recommends query parameters for filtering and sorting, including bracket-style comparison operators and a comma-separated `sort` parameter. Treat these as the guide’s preferred conventions rather than assuming every other syntax is inherently invalid. api_design_theoretical_deeprese…

### Examples

**Problematic proliferation:**

```text
GET /getPublishedArticles
GET /getDraftArticles
GET /getPublishedArticlesNewestFirst
```

**Preferred collection queries:**

```text
GET /v1/articles?status=published
GET /v1/articles?status=draft
GET /v1/articles?status=published&sort=-createdAt,title
```

In the last example, the proposed convention means descending creation time, then ascending title.

A more complex filter might be documented as:

```text
GET /v1/articles?createdAt[gte]=2026-01-01&status[in]=published,draft
```

An evaluator should be able to determine the supported fields, operators, value types, and combination rules without guessing.

### Feedback should explain

Identify endpoint-specific conventions and recommend consolidation where it accurately represents the domain.

**Example feedback:**

> Articles use `sort=-createdAt`, users use `orderBy=createdAt&descending=true`, and comments use `sortDirection=desc`. Select one sorting vocabulary, document supported fields and directions, and apply it consistently. Explain how clients should migrate from existing alternatives.

**Re-evaluation check:** Test individual filters, combined filters, ascending and descending sorting, multiple sort fields, and the documented behavior for unsupported parameters.

---

## 6. Pagination and Large-Collection Scalability

### What to assess

Evaluate pagination against the collection’s expected size and rate of change.

Check whether potentially large collections are paginated, limits are bounded, ordering is deterministic, and continuation information is sufficient to retrieve subsequent results.

The guide favors cursor pagination for high-volume or rapidly changing collections, while allowing offset pagination where its performance and traversal limitations are acceptable. api_design_theoretical_deeprese…

### Examples

Consider an offset-paginated collection ordered:

```text
A, B, C, D
```

The first page returns `A, B`. Before the next request, a new item `X` is inserted at the beginning:

```text
X, A, B, C, D
```

A request using `offset=2` now returns `B, C`. The consumer sees `B` twice.

A proposed cursor interface could instead use:

```text
GET /v1/articles?limit=50
```

The response supplies a continuation token, which the client passes unchanged:

```text
GET /v1/articles?limit=50&after=opaque-token
```

The contract should explain ordering, continuation, page-size limits, and how the client recognizes the final page. Test behavior during concurrent changes rather than assuming the presence of a cursor proves correctness.

### Feedback should explain

Connect the recommendation to the collection’s actual growth, volatility, and access patterns.

**Example feedback:**

> The activity feed uses deep offsets despite frequent insertion of new records. This can repeat or skip results during traversal. Introduce cursor pagination with deterministic ordering, such as creation time plus a unique identifier, and document behavior while the collection changes.

**Re-evaluation check:** Traverse a representative dataset, exercise equal sort values, insert or remove records between requests, and inspect deep-page performance. A small, bounded administrative table may reasonably retain offsets.

---

## 7. Response Shaping and Relationship Retrieval

### What to assess

For large or relationship-heavy resources, evaluate whether clients can avoid excessive transfer and excessive request counts.

Consider sparse field selection, explicit relationship expansion, and documented limits on expansion. The research presents these as ways to reduce over-fetching and multiple dependent requests. api_design_theoretical_deeprese…

Do not require these features where the payloads are already small and the relationships simple.

### Examples

Suppose a client needs only article identifiers and titles, but every response includes the full article body and extensive metadata.

A useful field-selection option could be:

```http
GET /v1/articles/93?fields=id,title
```

```json
{
  "id": 93,
  "title": "Designing Better APIs"
}
```

For a screen that also needs the author, an expansion option could be:

```http
GET /v1/articles/93?include=author
```

The response would contain the author representation instead of requiring a separate author request.

However, `include=comments` should not silently embed an unlimited comment history. The contract should explain any limits and how additional related results are retrieved.

### Feedback should explain

Identify the actual consumer burden and recommend only capabilities that address it.

**Example feedback:**

> The article-list screen needs titles and author names, but currently retrieves full article bodies and then makes one author request per result. Provide a lightweight field selection and a bounded author expansion, or another documented representation that supports this use case without unnecessary data transfer.

**Re-evaluation check:** Compare representative client workflows before and after the change, checking response size, request count, and documented expansion limits.

---

## 8. Standardized Error Responses

### What to assess

Evaluate whether errors use a consistent, machine-readable representation.

The preferred model is RFC 9457 Problem Details with `application/problem+json`. Assess meaningful use of `type`, `title`, `status`, `detail`, and `instance`.

In particular, `type` should identify the problem category for software, while `detail` explains the occurrence to a person. `instance` can identify an occurrence for diagnostic correlation. Consumers should not need to parse message wording to classify an error. api_design_theoretical_deeprese…

### Examples

**Problematic inconsistency:**

```json
{"error": "Article missing"}
```

Elsewhere:

```json
{"success": false, "message": "No such user"}
```

And elsewhere:

```json
{"error_code": 123, "description": "Failed"}
```

**Preferred consistent representation:**

```http
HTTP/1.1 404 Not Found
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/article-not-found",
  "title": "Article not found",
  "status": 404,
  "detail": "Article 93 does not exist.",
  "instance": "/problem-occurrences/request-abc123"
}
```

The client can branch on the problem type without depending on the wording of “Article 93 does not exist.”

**Standards clarification:** RFC 9457 does not require all five standard members in every response. Assess usefulness and the API’s documented problem contract; do not declare an error noncompliant merely because an optional member is absent. [RFC Editor](https://www.rfc-editor.org/rfc/rfc9457.html)

### Feedback should explain

Describe both the client-parsing burden and the missing diagnostic information.

**Example feedback:**

> Missing-resource errors have three different shapes across the API. Adopt a shared Problem Details representation and stable problem types. Keep occurrence-specific explanations in `detail`, so changing message wording does not break client error handling.

**Re-evaluation check:** Compare representative validation, authentication, authorization, missing-resource, and server-error responses for consistent handling.

---

## 9. Validation Error Quality

### What to assess

Evaluate whether consumers receive enough structured information to correct invalid requests.

Responses should identify relevant invalid fields where practical, their exact locations, and the reason each failed. Integrate these details into the standard error representation rather than combining everything into one unstructured message.

The guide recommends an extension such as `errors` or `invalid-params`, with precise locations such as JSON Pointers. api_design_theoretical_deeprese…

### Examples

Suppose an order request contains:

```json
{
  "email": "not-an-email",
  "items": [
    {"quantity": 1},
    {"quantity": 0}
  ]
}
```

**Insufficient feedback:**

```json
{"error": "Invalid request"}
```

**More useful feedback:**

```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation failed",
  "status": 422,
  "errors": [
    {
      "pointer": "/email",
      "code": "invalid_format",
      "detail": "Must be a valid email address."
    },
    {
      "pointer": "/items/1/quantity",
      "code": "below_minimum",
      "detail": "Must be at least 1."
    }
  ]
}
```

Here, the pointer identifies the second item’s quantity. The `errors`, `pointer`, and `code` fields are an illustrative extension design, not universal RFC-required field names.

### Feedback should explain

Specify which correction information is missing and how structured locations help clients associate errors with input fields.

**Example feedback:**

> The order endpoint reports only “Invalid request,” even when several independently identifiable fields fail validation. Return structured errors containing each field location, a stable error code, and the violated constraint. Document the extension schema alongside the request schema.

**Re-evaluation check:** Submit multiple invalid fields and nested-array errors. Confirm that the reported locations identify the actual failures and that corrections produce an accepted request.

---

## 10. Concurrency Protection

### What to assess

For resources that multiple actors can edit, determine whether the API protects against lost updates.

The guide’s preferred optimistic-concurrency pattern returns an `ETag`, accepts or requires `If-Match` on modification, compares that value with the current version, and rejects stale updates with `412 Precondition Failed`. api_design_theoretical_deeprese…

Inspect whether clients can bypass the protection by omitting the precondition. Do not require this mechanism for immutable resources or situations where concurrent editing is not relevant.

### Examples

A lost-update scenario:

```text
Client A reads article version 7.
Client B reads article version 7.
Client B saves changes, creating version 8.
Client A saves its older copy and overwrites B's changes.
```

A protected update would have Client A submit:

```http
PATCH /v1/articles/93
If-Match: "article-93-v7"
Content-Type: application/merge-patch+json

{"title": "Client A's revised title"}
```

Because version 8 now exists, the API rejects this stale update with `412`, preserving Client B’s changes. Client A must retrieve the current representation before resolving the conflict.

### Feedback should explain

Describe the actual overwrite scenario and where version information belongs in the interaction.

**Example feedback:**

> Two editors can read the same article and silently overwrite each other’s changes. Return a version validator when the article is retrieved, require the agreed precondition on updates, and reject stale writes. Document what happens when the precondition is omitted.

**Re-evaluation check:** Use two clients to reproduce the sequence. Confirm that stale writes do not change the resource and that simultaneous updates cannot both overwrite the same version unnoticed.

---

## 11. Retry Safety and Idempotency

### What to assess

Evaluate how mutations behave when clients retry after timeouts, connection failures, or ambiguous outcomes.

For operations with meaningful duplicate side effects, inspect whether an idempotency mechanism prevents duplicate execution, handles simultaneous retries, returns the original result for equivalent requests, detects key reuse with a different payload, defines retention, and handles partial execution or recovery.

The guide emphasizes that the client may not know whether a timed-out operation already succeeded. api_design_theoretical_deeprese…

### Examples

A client submits a test payment:

```http
POST /v1/payments
Idempotency-Key: c0988f1c-7222-4f8f-9bd7-04f545a98081
Content-Type: application/json

{"amount": 1000, "currency": "USD"}
```

The payment is created, but the response is lost. The client retries the same request with the same key.

**Problematic behavior:** A second payment is created.

**Preferred behavior:** The existing outcome is returned without executing the payment again.

Now change the amount while retaining the key:

```json
{"amount": 2000, "currency": "USD"}
```

The API should reject the inconsistent reuse rather than silently processing it or returning an unrelated cached result.

### Feedback should explain

Describe the duplicate-effect scenario and the full retry contract—not merely the presence of a header.

**Example feedback:**

> The payment endpoint accepts an idempotency key but still executes simultaneous requests with that key independently. Make duplicate prevention atomic, compare the request payload with the original, and document in-progress, completed, and recovery behavior. Specify how long retries remain protected.

**Re-evaluation check:** Test sequential duplicates, simultaneous duplicates, altered payloads, lost responses, and applicable recovery scenarios. Verify the underlying side effect occurred only once.

---

## 12. Long-Running Operation Design

### What to assess

For operations that may exceed reasonable synchronous request durations, evaluate whether the API uses an asynchronous request-reply workflow.

Look for prompt acceptance, `202 Accepted`, a `Location` identifying a job or status resource, understandable progress and terminal states, polling guidance such as `Retry-After`, and a clear route to the final result. The guide also permits a `303 See Other` redirect to that result. api_design_theoretical_deeprese…

### Examples

**Problematic:** A report-generation request holds the connection open for several minutes. A timeout leaves the client uncertain whether the report is still being generated.

**Preferred acceptance:**

```http
HTTP/1.1 202 Accepted
Location: /v1/jobs/job-17
Retry-After: 5
Content-Type: application/json

{"id": "job-17", "status": "queued"}
```

The client checks:

```http
GET /v1/jobs/job-17
```

The job contract defines states such as `queued`, `running`, `completed`, and `failed`. On successful completion, it supplies the report location or redirects to it:

```http
HTTP/1.1 303 See Other
Location: /v1/reports/report-93
```

### Feedback should explain

Identify why synchronous processing is fragile and whether clients can determine their next action throughout the asynchronous lifecycle.

**Example feedback:**

> Report generation can outlive the request timeout, but no status resource is available. Return 202 with a job location, document polling intervals and terminal states, and expose either the completed report or a structured failure. A failed job must not remain indistinguishable from a running job.

**Re-evaluation check:** Exercise successful and failed jobs. Confirm that clients can identify completion, obtain the result, and stop polling after a terminal outcome.

---

## 13. Rate Limiting and Backoff Behavior

### What to assess

Evaluate both server protection and client usability.

Where rate limiting is appropriate, verify actual enforcement, `429` responses, useful retry guidance, consistent quota information, and proactive quota visibility where supported.

The research recommends `Retry-After` and illustrates `RateLimit-Policy` and `RateLimit` headers for communicating quota policy and current availability. api_design_theoretical_deeprese…

### Examples

**Problematic:**

```http
HTTP/1.1 429 Too Many Requests

Too many requests.
```

The response leaves clients guessing when another attempt is appropriate.

**Preferred under this guide:**

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 30
Content-Type: application/problem+json

{
  "type": "https://api.example.com/problems/rate-limit-exceeded",
  "title": "Rate limit exceeded",
  "status": 429
}
```

The research’s illustrated quota-header convention is:

```http
RateLimit-Policy: "default";q=100;w=60
RateLimit: "default";r=42;t=15
```

The documentation should identify the adopted header specification or draft version and explain its units and scope. Do not treat the research’s draft syntax as an unstated, universal requirement.

**Standards clarification:** RFC 6585 permits, but does not mandate, `Retry-After` on a 429 response. This framework asks for it as a client-usability recommendation. [RFC Editor](https://www.rfc-editor.org/rfc/rfc6585.html)

### Feedback should explain

Explain what information clients lack and identify inconsistent limits or endpoint-specific header conventions.

**Example feedback:**

> The API enforces a quota but provides no retry guidance. Add a documented backoff signal, explain which requests share the quota, and use consistent quota headers where exposed.

**Re-evaluation check:** Exceed a controlled test quota, inspect the response, and confirm that documented backoff and quota behavior match implementation.

---

## 14. Authentication Architecture

### What to assess

For protected APIs, evaluate whether authentication uses established mechanisms rather than proprietary credential handling.

Where OAuth 2.0/OIDC is used, inspect the separation between token issuance and the API’s resource-server responsibilities. Where JWT access tokens are accepted, verify signature validation, expiration, applicable not-before checks, audience, issuer, and appropriate key retrieval and caching. api_design_theoretical_deeprese…

These checks are part of authentication assessment, not a complete security audit.

### Examples

A JWT’s readable payload is not evidence that the token is trustworthy. In an authorized test environment, distinguish these cases:

| Test token | Expected evaluation |
|---|---|
| Valid signature, trusted issuer, correct audience, valid time window | May proceed to authorization. |
| Altered payload without a valid corresponding signature | Must not be accepted as authentic. |
| Expired token | Must not be accepted as currently valid. |
| Token with a future `nbf` | Must not be accepted before its allowed time, subject to the documented clock-skew policy. |
| Validly signed token intended for another API | Must fail the receiving API’s audience check. |
| Token from an untrusted issuer | Must fail the issuer/trust check. |

These tests operationalize the guide’s required validation checks. api_design_theoretical_deeprese…

**Standards clarification:** OAuth does not require JWT-formatted access tokens. Do not fail an otherwise appropriate authentication architecture merely because it uses opaque tokens. [RFC Editor](https://www.rfc-editor.org/rfc/rfc6749.html)

### Feedback should explain

Identify each missing check and connect it to the misuse it prevents.

**Example feedback:**

> The API verifies signatures but does not validate the intended audience. A token issued for another service could therefore be accepted here. Configure the expected audience and add a negative test using an otherwise valid token for a different API.

Audience validation and explicit restrictions on accepted cryptographic algorithms are also addressed in the JWT security guidance. [RFC Editor](https://www.rfc-editor.org/rfc/rfc8725.html?utm_source=chatgpt.com)

**Re-evaluation check:** Inspect configuration and negative-test evidence. Successful login alone is not sufficient evidence of complete token validation.

---

## 15. Authorization and Scope Design

### What to assess

Determine whether authenticated callers are explicitly authorized for each operation.

Check operation-to-permission mappings, least privilege, consistent scope naming, meaningful business boundaries, and consistent rejection of insufficient permissions. Avoid scopes that are either excessively broad or unnecessarily fragmented.

The research recommends understandable resource/action conventions such as `read:users` and `write:articles`. api_design_theoretical_deeprese…

### Examples

Suppose a token has only:

```text
read:articles
```

A clear permission model might allow:

```http
GET /v1/articles/93
```

but reject:

```http
PATCH /v1/articles/93
```

The update requires `write:articles`.

**Overly broad design:** Every consumer needs a single `admin` scope, even to retrieve articles.

**Overly fragmented design:** Similar operations require unrelated names such as `editArticleTitle`, `modify_article_body`, and `article-update-tags`, without a meaningful reason for those boundaries.

**Standards clarification:** In OAuth bearer-token usage, an invalid token and insufficient scope are different conditions: invalid tokens generally produce 401; insufficient scope generally produces 403. [RFC Editor](https://www.rfc-editor.org/rfc/rfc6750.html?utm_source=chatgpt.com)

### Feedback should explain

Identify the missing capability boundary and how the permission model should express it.

**Example feedback:**

> Read-only consumers must obtain the same scope as editors. Introduce a distinct read capability and enforce write permission on mutation endpoints. Document required scopes per operation and keep naming consistent across resources.

**Re-evaluation check:** Use tokens with no relevant scope, read-only scope, and write scope. Test equivalent operations across resource types, not only one endpoint.

---

## 16. OpenAPI Contract Completeness

### What to assess

Evaluate whether the formal contract accurately describes the externally observable interface.

Inspect every public operation, request parameter, request body, response body, error response, status code, security requirement, reusable schema, relevant header, and data constraint.

The research advocates API-first design and emphasizes OpenAPI 3.1’s alignment with JSON Schema. A consumer should not need implementation access to discover essential behavior. api_design_theoretical_deeprese… api_design_theoretical_deeprese…

### Examples

**Insufficient response documentation:**

```yaml
responses:
  "200":
    description: Success
```

For an endpoint that returns a structured JSON user, this does not tell consumers what the payload contains.

**More informative response excerpt:**

```yaml
responses:
  "200":
    description: User retrieved successfully.
    content:
      application/json:
        schema:
          $ref: "#/components/schemas/User"
  "404":
    description: The requested user does not exist.
    content:
      application/problem+json:
        schema:
          $ref: "#/components/schemas/Problem"
```

This is an illustrative excerpt, not a complete operation. Its referenced schemas must also be defined.

Other gaps include an implemented `status` filter missing from the specification, undocumented rate-limit responses, or a creation endpoint that emits `Location` without describing it.

### Feedback should explain

Identify exactly where the contract is weaker than the interface.

**Example feedback:**

> `GET /v1/users/{id}` documents only a success description, although it returns a structured user and a structured 404 error. Add both response schemas and reconcile the operation against actual behavior. Document required parameters, authentication, and relevant headers in the same review.

**Re-evaluation check:** Compare route inventories and representative observed interactions against the specification. A syntactically valid OpenAPI file is not, by itself, evidence of completeness.

---

## 17. Schema Precision and Type Safety

### What to assess

Evaluate whether schemas describe the actual data contract precisely enough for validation and typed client generation.

Look for specific types, formats, constraints, required properties, accurate nullability, and consistent reuse of domain models. Avoid unrestricted objects where the API has a stable structure, while allowing genuinely dynamic maps where intended.

The guide emphasizes the distinction between an omitted property and a property whose value is explicitly null. api_design_theoretical_deeprese…

### Examples

**Too weak for a stable user representation:**

```yaml
User:
  type: object
```

**More precise illustrative schema:**

```yaml
User:
  type: object
  required: [id, email, deletedAt]
  properties:
    id:
      type: integer
      minimum: 1
    email:
      type: string
      format: email
    deletedAt:
      type: ["string", "null"]
      format: date-time
    nickname:
      type: string
    biography:
      type: ["string", "null"]
```

This deliberately illustrates four different contracts:

| Property | May be omitted? | May be null? |
|---|---:|---:|
| `email` | No | No |
| `deletedAt` | No | Yes |
| `nickname` | Yes | No |
| `biography` | Yes | Yes |

For OpenAPI 3.1, use JSON Schema nullability rather than relying on the older `nullable: true` convention. api_design_theoretical_deeprese…

### Feedback should explain

Identify the exact weak schemas and explain their consequences for validation and generated clients.

**Example feedback:**

> The `User` schema is an unrestricted object even though the response has stable fields. Define the properties and their types, identify required fields, and distinguish optional from nullable values. Otherwise, consumers cannot reliably infer which properties exist or what values they contain.

**Re-evaluation check:** Validate representative valid and invalid payloads, explicitly test omission versus null, and inspect the resulting client types.

---

## 18. Operation Naming and SDK Usability

### What to assess

Evaluate whether every operation has an explicit, unique, meaningful `operationId` that uses consistent domain language and produces understandable client methods.

The guide connects operation naming directly to generated SDK usability. api_design_theoretical_deeprese…

### Examples

| Operation | Weak or mechanically derived name | Suggested `operationId` |
|---|---|---|
| `GET /v1/users` | `getV1Users` | `listUsers` |
| `GET /v1/users/{id}` | `usersGetById` | `getUser` |
| `POST /v1/users` | `postUsers` | `createUser` |
| `PATCH /v1/users/{id}` | `patchUserEndpoint` | `updateUser` |
| `DELETE /v1/users/{id}` | `deleteV1UsersId` | `deleteUser` |

A duplicate `operationId` on two different operations is a separate issue from awkward wording.

**Standards clarification:** OpenAPI makes `operationId` optional, but requires uniqueness when supplied. Requiring it on every operation is this guide’s SDK-usability convention, not a prerequisite for every valid OpenAPI document. [OpenAPI Specification](https://spec.openapis.org/oas/v3.1.1.html)

### Feedback should explain

Show the intended client-facing names and identify any generated-code problems.

**Example feedback:**

> Several operations lack operation IDs, and two share `getUser`. Assign unique, domain-oriented IDs such as `listUsers` and `getUser`, then generate the intended SDK and verify that its methods remain distinguishable without manual renaming.

**Re-evaluation check:** Check uniqueness, generate the target client, and build a small client example. Inspect method names, request types, and response types rather than relying on successful generation alone.

---

## 19. Polymorphic Schema Design

### What to assess

Where an operation accepts or returns structurally different variants, determine whether clients can identify and validate the correct variant reliably.

The guide prefers `oneOf` with a discriminator property and appropriate mappings. Its concern is ambiguity that makes generated types or deserialization unreliable. api_design_theoretical_deeprese…

### Examples

Suppose an asset may be text or an image.

**Ambiguous design:** Both schemas have mostly optional properties and no reliable type indicator. A payload such as `{"id": 17}` could match either schema.

**Clearer payloads:**

```json
{"kind": "text", "text": "Welcome"}
```

```json
{"kind": "image", "imageUrl": "https://example.com/banner.png"}
```

An illustrative schema excerpt, placed under `components.schemas`, is:

```yaml
Asset:
  oneOf:
    - $ref: "#/components/schemas/TextAsset"
    - $ref: "#/components/schemas/ImageAsset"
  discriminator:
    propertyName: kind
    mapping:
      text: "#/components/schemas/TextAsset"
      image: "#/components/schemas/ImageAsset"

TextAsset:
  type: object
  required: [kind, text]
  properties:
    kind:
      type: string
      const: text
    text:
      type: string

ImageAsset:
  type: object
  required: [kind, imageUrl]
  properties:
    kind:
      type: string
      const: image
    imageUrl:
      type: string
      format: uri
```

**Standards clarification:** `anyOf` is not inherently invalid; it permits overlapping matches. A discriminator does not itself change schema-validation results, so each variant still needs appropriate constraints. [OpenAPI Specification](https://spec.openapis.org/oas/v3.1.1.html)

### Feedback should explain

Identify which payloads are ambiguous, propose a discriminating field, and explain the client impact.

**Example feedback:**

> Asset variants can match the same minimal payload, leaving clients unable to select a type reliably. Require a stable `kind` value, constrain each variant accordingly, and document explicit mappings. Do not assume adding a discriminator alone resolves overlapping schemas.

**Re-evaluation check:** Test each valid variant, missing and unknown discriminator values, and payloads whose discriminator conflicts with their content.

---

## 20. Contract Testing and Breaking-Change Protection

### What to assess

Determine whether the contract is enforced through automated tests and release processes.

Assess provider conformance, protection of important consumer interactions, detection of incompatible changes, CI/CD integration, and whether specification changes are reviewed as part of delivery rather than afterward.

The guide recommends consumer-driven contract testing to detect incompatibilities before deployment. api_design_theoretical_deeprese…

### Examples

An existing consumer expects:

```json
{"id": 42, "email": "riley@example.com"}
```

A proposed release changes the same field:

```json
{
  "id": 42,
  "email": {
    "address": "riley@example.com",
    "verified": true
  }
}
```

The field name is unchanged, but a consumer expecting a string no longer receives its agreed representation.

Another example is making a previously optional request field mandatory without updating or migrating existing callers.

**Insufficient protection:** The new provider tests pass because they were rewritten to expect the new representation.

**Stronger protection:** Compatibility checks and representative consumer tests identify that supported clients still depend on the previous contract.

### Feedback should explain

Describe the incompatible change that could escape the current process and identify where the release should be stopped.

**Example feedback:**

> The pipeline validates the new implementation but does not check compatibility with supported consumers. Add checks against their agreed contracts, including field types and required request properties. An incompatible change should require an explicit migration or versioning decision before release.

**Re-evaluation check:** Introduce a deliberate breaking change in a test branch and verify that the relevant release check fails. Also verify that an intended compatible change can proceed.

---

## 21. Webhook Contract Quality

### What to assess

Apply this criterion only to APIs that publish webhook events.

Treat webhook consumers as API consumers. Inspect event types, payload schemas, headers, authentication or signature requirements, expected receiver responses, and documented retry behavior.

The guide describes OpenAPI’s top-level `webhooks` construct as a way to make server-initiated interactions part of the formal contract. api_design_theoretical_deeprese…

### Examples

**Insufficient documentation:**

> “We send a webhook when a comment is created.”

This leaves the receiver to discover the payload, verification method, acknowledgement, and redelivery behavior.

**More useful illustrative event:**

```json
{
  "event_id": "evt-123",
  "event_type": "comment.created",
  "occurred_at": "2026-01-01T12:00:00Z",
  "data": {
    "comment_id": 17,
    "article_id": 93
  }
}
```

An accompanying example contract might specify that the receiver returns `204` to acknowledge delivery, that a named signature header must be verified, and that repeated delivery retains the same `event_id`.

Those are illustrative policy choices. The API must document its actual signature construction, acknowledgement rules, retry conditions, and limits rather than leaving them implicit.

### Feedback should explain

Identify what receivers would otherwise need to reverse-engineer.

**Example feedback:**

> The `comment.created` webhook lacks a formal schema and verification instructions. Document required fields, signature headers and verification procedure, accepted acknowledgement responses, and redelivery behavior. Provide a sample event and explain how a receiver recognizes repeated delivery.

**Re-evaluation check:** Deliver a test event to a receiver built from the documentation. Exercise valid acknowledgement, failure or timeout, and applicable signature-validation cases.

---

## 22. API-Wide Consistency and Predictability

### What to assess

Evaluate the API as a complete product, not merely as individually acceptable endpoints.

A consumer who learns one area should be able to predict equivalent behavior elsewhere. Compare URI naming, methods, status codes, filtering, sorting, pagination, errors, authentication, scopes, schemas, update semantics, headers, and asynchronous workflows.

Predictability is a central principle of the research. api_design_theoretical_deeprese…

### Examples

Suppose the collection endpoints use:

```text
GET /v1/users?limit=50
GET /v1/articles?pageSize=50
GET /v1/comments?maxResults=50
```

Each might be usable alone, but together they force consumers to learn three names for the same concept.

Likewise, one collection might return:

```json
{"data": [], "next_cursor": null}
```

while another returns:

```json
{"results": [], "pagination": {"next": null}}
```

The issue is not necessarily that either structure is intrinsically wrong. It is that equivalent operations follow different conventions without a clear reason.

Similar inconsistency can appear in error schemas, timestamp representations, permission names, update behavior, or job states.

### Feedback should explain

Identify the underlying design rule and group repeated instances into a coherent finding. Avoid reporting the same systemic issue as dozens of unrelated defects.

**Example feedback:**

> Collection pagination uses `limit`, `pageSize`, and `maxResults` for equivalent controls. Adopt one vocabulary and document any justified exceptions. Update the shared contract components, implementation helpers, examples, and tests so the convention applies to future endpoints as well as existing ones.

**Re-evaluation check:** Review representative operations across every resource family and trace at least one complete consumer workflow. Confirm that the correction is API-wide rather than limited to the endpoint named in the original finding.
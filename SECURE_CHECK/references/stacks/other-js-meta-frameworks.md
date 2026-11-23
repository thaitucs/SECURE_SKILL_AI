# Other JS frameworks (Astro, Remix / React Router, Gatsby, SolidStart, Qwik)

**Common rule:** find what runs on the server (loaders, actions, endpoints, server functions)
and treat it as `BE`; everything sent to the browser is `FE`.

| Framework | Server code | Public env |
|-----------|-------------|-----------|
| Astro | `src/pages/**/*.ts` endpoints, frontmatter of `.astro` in SSR mode, actions | `PUBLIC_*` |
| Remix / React Router v7 | `loader`, `action`, `*.server.ts` | `window.ENV` you choose to expose |
| Gatsby | `gatsby-node.js`, Functions `src/api/` | `GATSBY_*` |
| SolidStart | `"use server"` functions, API routes | `VITE_*` |
| Qwik City | `routeLoader$`, `routeAction$`, `server$` | `PUBLIC_*` |

**Top risks:** actions/server functions without auth; loaders returning sensitive fields;
`set:html` (Astro) / `dangerouslySetInnerHTML`; secrets with public prefix; static builds
containing data meant to be private (Gatsby/Astro SSG bake data into HTML).

**Target mapping:** keep framework routes; put logic in `src/server/services`,
`src/server/policies`, `src/server/db`, `src/server/storage` (mark server-only).

**Verify:** the framework's `build` command; grep the output folder for secrets.

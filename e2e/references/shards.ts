/**
 * The suite's projects and the CI shards that split them. Plain data with no runtime import, so
 * `shard-key.ts` can read it with bare Bun or Node before a package is installed.
 * `playwright.config.ts` takes its projects from `projectsFor(process.env.E2E_SHARD)`.
 *
 * Replace the example projects with your own. Order matters only where projects share state.
 */
export type ProjectSpec = { name: string; testMatch: RegExp; dependencies?: string[] };

export const PROJECTS: ProjectSpec[] = [
  // Read-only projects first: they read the seed and change nothing shared.
  { name: "routes", testMatch: /\/routes\.e2e\.ts$/ },
  { name: "api", testMatch: /\/api\.e2e\.ts$/ },
  { name: "flows", testMatch: /\/(flows|admin)\.e2e\.ts$/, dependencies: ["routes"] },
  // Restores the seeded data: nothing else may edit it meanwhile.
  { name: "restore", testMatch: /\/restore\.e2e\.ts$/, dependencies: ["flows"] },
  // Clicks every control: runs after the projects that read seeded state.
  { name: "crawl", testMatch: /\/crawl\.e2e\.ts$/, dependencies: ["restore"] },
  // The one project on the production build.
  { name: "bundle", testMatch: /\/bundle\.e2e\.ts$/, dependencies: ["restore"] },
];

/** One CI job per shard, on its own runner with its own services and a fresh instance. */
export const SHARDS = {
  read: ["routes", "api"],
  flows: ["flows"],
  write: ["restore", "bundle"],
  crawl: ["crawl"],
} as const satisfies Record<string, readonly string[]>;

export type Shard = keyof typeof SHARDS;

export function isShard(name: string): name is Shard {
  return Object.hasOwn(SHARDS, name);
}

/** The projects in the shard that `name` waits for, directly or through projects outside it. */
function nearestInShard(name: string, inShard: ReadonlySet<string>): string[] {
  const project = PROJECTS.find((one) => one.name === name);
  return (project?.dependencies ?? []).flatMap((dependency) =>
    inShard.has(dependency) ? [dependency] : nearestInShard(dependency, inShard)
  );
}

/** Every project for a full run, or one shard's projects with the chain order kept inside it. */
export function projectsFor(shard: string | undefined): ProjectSpec[] {
  if (shard === undefined || shard === "") return PROJECTS;
  if (!isShard(shard)) throw new Error(`E2E_SHARD=${shard} is not one of ${Object.keys(SHARDS).join(", ")}`);
  const inShard = new Set<string>(SHARDS[shard]);
  return PROJECTS.filter((project) => inShard.has(project.name)).map((project) => ({
    ...project,
    dependencies: [...new Set(nearestInShard(project.name, inShard))],
  }));
}

const SPEC = /^e2e\/[^/]+\.e2e\.ts$/;

/** The shards whose projects run a spec file, by its path from the repository root. */
export function shardsOfSpec(path: string): Shard[] {
  const projects = new Set(PROJECTS.filter((p) => p.testMatch.test(`/${path}`)).map((p) => p.name));
  return Object.keys(SHARDS)
    .filter(isShard)
    .filter((shard) => SHARDS[shard].some((name) => projects.has(name)));
}

/**
 * The tracked files a shard's result depends on: all but other shards' specs and what no shard
 * reads. Leaving out `docs/` and Markdown is one project's choice; keep any folder your app is
 * served from.
 */
export function inputsOf(shard: Shard, tracked: readonly string[]): string[] {
  return tracked.filter((path) => {
    if (path.startsWith("docs/") || path.endsWith(".md")) return false;
    if (!SPEC.test(path)) return true;
    return shardsOfSpec(path).includes(shard);
  });
}

/*
 * The test that keeps the table honest (shards.test.ts):
 *
 *   test("every project and every spec belongs to a shard", () => {
 *     const sharded = new Set(Object.values(SHARDS).flat());
 *     expect(PROJECTS.map((p) => p.name).filter((n) => !sharded.has(n))).toEqual([]);
 *     const specs = readdirSync("e2e").filter((f) => f.endsWith(".e2e.ts")).map((f) => `e2e/${f}`);
 *     expect(specs.filter((s) => shardsOfSpec(s).length === 0)).toEqual([]);
 *   });
 */

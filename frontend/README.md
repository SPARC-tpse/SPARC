# SPARC Frontend

## Developer setup

Prerequisites:
- node.js
- npm

Install dependencies
```bash
npm install
```

## Run

### without Docker

Start the dev server with hot-reload
```bash
npm run dev
```

### Docker

Build and start frontend dev container
```bash
docker compose up frontend --build
```

## Tests

Do the [manuel tests](manuel_tests.md) discripted in the markdown.

## Project Structure
```bash
tree -I "node_module" --dirsfirst
```
```
.
├── app
│   ├── assets
│   │   └── css
│   │       └── tailwind.css            |
│   ├── components
│   │   ├── widgets                     |
│   │   │   ├── DashboardWidget.vue     |
│   │   │   ├── DisruptionsWidget.vue   |
│   │   │   ├── GanttWidget.vue         |
│   │   │   ├── KPIWidget.vue           |
│   │   │   ├── OrderGanttWidget.vue    |
│   │   │   ├── OrdersWidget.vue        |
│   │   │   ├── ProcessGanttWidget.vue  |
│   │   │   ├── ResourceGanttWidget.vue |
│   │   │   └── ResourcesWidget.vue     |
│   │   ├── DashboardAddPanel.vue       |
│   │   ├── DashboardGrid.vue           |
│   │   ├── DisruptionTimerPopout.vue   |
│   │   ├── FileUpload.vue              |
│   │   ├── MultiSelect.vue             |
│   │   ├── Navbar.vue                  |
│   │   ├── ProcessTimer.vue            |
│   │   ├── Topbar.vue                  |
│   │   └── WorkerMultiSelect.vue       |
│   ├── composables
│   │   ├── useAppTheme.js              |
│   │   ├── useDashboardData.ts         |
│   │   ├── useDashboardLayout.ts       |
│   │   ├── useDisruptionDraft.ts       |
│   │   ├── useDisruptionTimer.ts       |
│   │   ├── useOrderDraft.ts            |
│   │   ├── useOrderWebSocket.js        |
│   │   ├── useResourceDraft.ts         |
│   │   ├── useTheme.js                 |
│   │   ├── useWorkerDraft.ts           |
│   │   └── useZoom.ts                  |
│   ├── layouts
│   │   └── custom.vue                  |
│   ├── pages
│   │   ├── dashboard
│   │   │   ├── gantt
│   │   │   │   └── [id].vue            |
│   │   │   ├── index.vue               |
│   │   │   └── old.vue                 |
│   │   ├── disruption
│   │   │   ├── edit
│   │   │   │   └── [id].vue            |
│   │   │   ├── index.vue               |
│   │   │   ├── new.vue                 |
│   │   │   └── overview.vue            |
│   │   ├── order
│   │   │   ├── edit
│   │   │   │   └── [id].vue            |
│   │   │   ├── index.vue               |
│   │   │   ├── new.vue                 |
│   │   │   └── overview.vue            |
│   │   ├── resource
│   │   │   ├── edit
│   │   │   │   └── [id].vue            |
│   │   │   ├── index.vue               |
│   │   │   ├── new.vue                 |
│   │   │   └── overview.vue            |
│   │   ├── worker
│   │   │   ├── edit
│   │   │   │   └── [id].vue            |
│   │   │   ├── index.vue               |
│   │   │   ├── new.vue                 |
│   │   │   └── overview.vue            |
│   │   └── index.vue                   |
│   └── app.vue                         |
├── public
│   ├── favicon.ico
│   └── robots.txt                      |
├── Dockerfile                          |
├── manuel_tests.md                     |
├── nuxt.config.ts                      |
├── package.json                        |
├── package-lock.json                   |
├── postcss.config.cjs                  |
├── README.md                           |
├── tailwind.config.cjs                 |
└── tsconfig.json                       |
```

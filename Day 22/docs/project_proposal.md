# Project Proposal

## Project
**E-commerce Analytics & Data Intelligence Platform**

## Problem statement
Sales, customer, product, regional, and inventory information is often held in
separate operational sources. Inconsistent data and metric definitions make
business reporting difficult to reproduce.

## Goal
Design and build a learning-scale platform that ingests e-commerce data,
validates it, models it for analytics, and documents how business users can
consume it.

## Learning objectives
- Design the components and boundaries of a data platform.
- Plan a batch architecture and describe how it could evolve.
- Define source, volume, cadence, analytics, dashboard, and persona
requirements.
- Set up a repeatable development environment with PostgreSQL and Airflow.
- Deliver a project proposal, architecture, data model, ETL flow, task plan,
  and project README.

## Scope and assumptions
- Implemented source: synthetic CSV files in `data/sample/`.
- Processing: daily batch ETL orchestrated by Airflow, with an option to run
  directly from Python.
- Warehouse: PostgreSQL star schema with sales-line and inventory-snapshot
  facts.
- Visualization: Power BI design requirements and mockups; a finished report
  file is not included.
- Real-time inventory, live APIs, and website scraping are future extensions,
  not part of the current runnable pipeline.

## Success criteria
- The documented schema can be created in PostgreSQL.
- The sample CSV set can be validated and loaded without duplicate facts on a
  retry.
- Automated tests cover important validation and transformation behavior.
- The documentation explains requirements, architecture, model, ETL flow,
  dashboards, setup, and milestones.

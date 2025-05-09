
---
title: ChRIS Platform Overview
tags: [chris, medical imaging, plugins, architecture]
source: https://chrisproject.org/
type: documentation
---


# ChRIS Platform Overview

**ChRIS** (ChRIS Research Integration Service) is an open-source, distributed platform built to manage computation and data across diverse environments.

## Origin and Purpose

Originally developed at **Boston Children's Hospital** for medical image analysis, ChRIS has evolved into a general-purpose compute and data orchestration platform. It supports research workflows across a variety of domains, not limited to healthcare.

## Key Capabilities

ChRIS enables the deployment and execution of data processing pipelines on:

- Laptops and workstations  
- HPC (High-Performance Computing) clusters  
- Public and private cloud infrastructure  

It abstracts away infrastructure complexity so researchers can focus on their analyses.

## Application Characteristics

ChRIS primarily supports **non-interactive applications** that:

- Are containerized using **Linux-based containers**  
- Accept **command-line arguments** for configuration  
- Produce results in **output files**  
- Require no user interaction once started

These applications are referred to as **plugins** within ChRIS.

## User Interfaces

ChRIS provides:

- A **web-based graphical interface** for managing workflows  
- Multiple **REST APIs** for integration with automated systems  
- Support for frontends that allow users to monitor and control pipelines

## Plugins and Pipelines

A ChRIS plugin is a containerized tool that adheres to a standardized interface. Plugins can be chained together into **pipelines**, enabling modular and reusable workflows.

ChRIS plugins can perform tasks such as:

- Medical image processing  
- Machine learning inference  
- Data cleaning and transformation  
- Visualization and reporting

## System Architecture

ChRIS is composed of:

- **RESTful web services** for API-based orchestration  
- Backend services for job scheduling, storage, and compute coordination  
- Frontend components for user interaction  

The architecture simplifies the deployment of containerized tools across any Linux-compatible environment, ensuring portability and reproducibility.

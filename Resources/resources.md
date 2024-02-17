## Background

### Statistics of data center carbon emissions

- Overview about GHG & energy use of data centres and data transmission networks by IEA: https://www.iea.org/energy-system/buildings/data-centres-and-data-transmission-networks#tracking
- Recalibrating global data center energy-use estimates: https://datacenters.lbl.gov/sites/default/files/Masanet_et_al_Science_2020.full_.pdf
- Information and communications technology sector carbon footprint share 2020: https://www.statista.com/statistics/1255404/global-ict-products-relative-carbon-footprint-forecast-by-products/

## Related work

- [A Guide to Reducing Carbon Emissions through Data Center Geographical Load Shifting](https://dl.acm.org/doi/abs/10.1145/3447555.3466582): Use mathematical approaches and formulas to provide a guide to geographical datacenter load scheduling, but no analysis on the impacts on the applications' performance.
- [GA-Par: Dependable Microservice Orchestration Framework for Geo-Distributed Clouds](https://ieeexplore.ieee.org/abstract/document/8766876): Develop GA-Par, a framework to orchestrate microservices across geo-distributed clouds using mathematical approaches and formulas. Although data transmission latency is measured, the focus of this paper is application security on the cloud.
- [Stratus: Load Balancing the Cloud for Carbon Emissions Control](https://ieeexplore.ieee.org/abstract/document/6587037): Propose a graph-based Stratus system, Stratus, which utilises Voronoi partitions to determine which data centre requests should be routed to. It makes some trade-off among latency, carbon emissions and electricity cost.
- [Mitigating Curtailment and Carbon Emissions through Load Migration between Data Centers](https://www.sciencedirect.com/science/article/pii/S2542435120303470): Simulate the effect of migrating data center workloads from the fossil-fuel-heavy PJM to the renewable-heavy CAISO on greenhouse gas (GHG) emissions using historical hourly electricity generation, curtailment, and typical data center server utilization data. Also no analysis on the impacts on the applications' performance.
- [QoS-awareness of Microservices with Excessive Loads via Inter-Datacenter Scheduling](https://ieeexplore.ieee.org/abstract/document/9820678): Evaluate the performance of microservices with metrics of CPU usage and 99%-ile latency in the situation where some microservices of the applications are migrated to remote datacenters when the local datacenter does not have enough resources. Three open-sourced microservice benchmarks SocialNetwork, MediaService, and HotelReservation in the DeathStarBench are used for the experiment.

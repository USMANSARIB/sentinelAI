
import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface NetworkGraphProps {
  data: {
    nodes: any[];
    links: any[];
  };
}

export const NetworkGraph: React.FC<NetworkGraphProps> = ({ data }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const width = 600;
    const height = 400;
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const simulation = d3.forceSimulation(data.nodes as any)
      .force("link", d3.forceLink(data.links).id((d: any) => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg.append("g")
      .selectAll("line")
      .data(data.links)
      .enter().append("line")
      .attr("stroke", (d: any) => d.type === 'SIMILAR' ? '#ff0055' : '#00f2ff')
      .attr("stroke-opacity", 0.3)
      .attr("stroke-width", (d: any) => d.weight * 2);

    const node = svg.append("g")
      .selectAll("circle")
      .data(data.nodes)
      .enter().append("circle")
      .attr("r", (d: any) => 8 + (d.bot_score * 5))
      .attr("fill", (d: any) => {
        if (d.group === 'bot') return '#ff0055';
        if (d.group === 'organic') return '#00ff88';
        return '#00f2ff';
      })
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
      .call(d3.drag<SVGCircleElement, any>()
        .on("start", (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }));

    node.append("title").text((d: any) => `${d.handle} (Score: ${d.bot_score})`);

    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      node
        .attr("cx", (d: any) => d.x)
        .attr("cy", (d: any) => d.y);
    });

    return () => simulation.stop();
  }, [data]);

  return (
    <div className="relative w-full overflow-hidden bg-black/40 rounded border border-cyan-500/10">
      <svg ref={svgRef} viewBox={`0 0 600 400`} className="w-full h-auto" />
      <div className="absolute top-2 right-2 flex flex-col gap-1 text-[10px] mono">
        <div className="flex items-center"><span className="w-2 h-2 rounded-full bg-[#ff0055] mr-1"></span> BOT</div>
        <div className="flex items-center"><span className="w-2 h-2 rounded-full bg-[#00ff88] mr-1"></span> ORGANIC</div>
        <div className="flex items-center"><span className="w-2 h-2 rounded-full bg-[#00f2ff] mr-1"></span> ORIGIN</div>
      </div>
    </div>
  );
};

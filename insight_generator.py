def generate_executive_summary(portfolio, sector_df, stage_dist, health_issues):
    """
    Generates a natural language summary for a Founder.
    """
    total = portfolio['total_pipeline']
    weighted = portfolio['weighted_pipeline']
    count = portfolio['deal_count']
    
    # 1. Headline
    insight = f"### 🚀 Executive Summary\n"
    insight += f"You have **{count} active deals** with a total face value of **${total:,.0f}**.\n"
    insight += f"Based on deal probabilities, your **Risk-Adjusted Forecast is ${weighted:,.0f}**.\n\n"
    
    # 2. Sector Insights
    if sector_df is not None and not sector_df.empty:
        top_sector = sector_df.index[0]
        top_val = sector_df.iloc[0]['Value']
        insight += f"**📈 Top Performer:** The **{top_sector}** sector is leading with ${top_val:,.0f} in pipeline.\n"
        
    # 3. Stage/Bottleneck Insights
    if stage_dist is not None and not stage_dist.empty:
        stuck_stage = stage_dist.idxmax()
        stuck_count = stage_dist.max()
        insight += f"**🚧 Bottleneck:** The majority of your deals ({stuck_count}) are sitting in **'{stuck_stage}'**.\n\n"

    # 4. Data Resilience Warnings
    if health_issues:
        insight += "---\n**⚠ Data Health Check:**\n"
        for issue in health_issues:
            insight += f"- {issue}\n"
            
    return insight
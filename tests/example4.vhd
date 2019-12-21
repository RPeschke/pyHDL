entity tb_entity is 
end entity;



architecture rtl of tb_entity is

signal clkgen_clk : std_logic := '0'; 
signal maxCount : std_logic_vector(31 downto 0) := x"00000014"; 
signal pipe1_1_rollingCounter_Axi_out_m2s : axisStream_32_m2s := axisStream_32_m2s_null;
signal pipe1_1_rollingCounter_Axi_out_s2m : axisStream_32_s2m := axisStream_32_s2m_null;
signal pipe1_2_axiFilter_Axi_in_m2s : axisStream_32_m2s := axisStream_32_m2s_null;
signal pipe1_2_axiFilter_Axi_in_s2m : axisStream_32_s2m := axisStream_32_s2m_null;
signal pipe1_2_axiFilter_Axi_out_m2s : axisStream_32_m2s := axisStream_32_m2s_null;
signal pipe1_2_axiFilter_Axi_out_s2m : axisStream_32_s2m := axisStream_32_s2m_null;
signal pipe1_3_axiPrint_Axi_in_m2s : axisStream_32_m2s := axisStream_32_m2s_null;
signal pipe1_3_axiPrint_Axi_in_s2m : axisStream_32_s2m := axisStream_32_s2m_null;

begin
clkgen : entity work.clk_generator port map ( 
      clk => clkgen_clk
  );
  pipe1_1_rollingCounter : entity work.rollingCounter port map ( 
      Axi_out_m2s => pipe1_1_rollingCounter_Axi_out_m2s, 
      Axi_out_s2m => pipe1_1_rollingCounter_Axi_out_s2m,
      MaxCount => maxCount,
      clk => clkgen_clk
  );
    pipe1_2_axiFilter : entity work.axiFilter port map ( 
      Axi_in_m2s => pipe1_2_axiFilter_Axi_in_m2s, 
      Axi_in_s2m => pipe1_2_axiFilter_Axi_in_s2m,
      Axi_out_m2s => pipe1_2_axiFilter_Axi_out_m2s, 
      Axi_out_s2m => pipe1_2_axiFilter_Axi_out_s2m,
      clk => clkgen_clk
  );
    pipe1_3_axiPrint : entity work.axiPrint port map ( 
      Axi_in_m2s => pipe1_3_axiPrint_Axi_in_m2s, 
      Axi_in_s2m => pipe1_3_axiPrint_Axi_in_s2m,
      clk => clkgen_clk
  );
    ---------------------------------------------------------------------
  --  pipe1_2_axiFilter_Axi_in << pipe1_1_rollingCounter_Axi_out
  pipe1_2_axiFilter_Axi_in_m2s <= pipe1_1_rollingCounter_Axi_out_m2s;
  pipe1_1_rollingCounter_Axi_out_s2m <= pipe1_2_axiFilter_Axi_in_s2m;
    ---------------------------------------------------------------------
  --  pipe1_3_axiPrint_Axi_in << pipe1_2_axiFilter_Axi_out
  pipe1_3_axiPrint_Axi_in_m2s <= pipe1_2_axiFilter_Axi_out_m2s;
  pipe1_2_axiFilter_Axi_out_s2m <= pipe1_3_axiPrint_Axi_in_s2m;
  
end architecture;
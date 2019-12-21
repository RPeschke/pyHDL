entity tb_entity is 
end entity;



architecture rtl of tb_entity is

signal clkgen_clk : std_logic := '0'; 
signal Axi_out_m2s : axisStream_32_m2s := axisStream_32_m2s_null;
signal Axi_out_s2m : axisStream_32_s2m := axisStream_32_s2m_null;
signal counter : std_logic_vector(31 downto 0) := (others => '0'); 
signal axFil_Axi_in_m2s : axisStream_32_m2s := axisStream_32_m2s_null;
signal axFil_Axi_in_s2m : axisStream_32_s2m := axisStream_32_s2m_null;

begin
clkgen : entity work.clk_generator port map ( 
      clk => clkgen_clk
  );
  axFil : entity work.axiPrint port map ( 
      Axi_in_m2s => axFil_Axi_in_m2s, 
      Axi_in_s2m => axFil_Axi_in_s2m,
      clk => clkgen_clk
  );
  ---------------------------------------------------------------------
  --  axFil_Axi_in << Axi_out
  axFil_Axi_in_m2s <= Axi_out_m2s;
  Axi_out_s2m <= axFil_Axi_in_s2m;
  
  -----------------------------------
  p2 : process(clkgen_clk) is
    variable v_Axi_out : axisStream_32_master := axisStream_32_master_null;
    begin
      if rising_edge(clkgen_clk) then 
        pull( v_Axi_out, Axi_out_s2m);
    
        if (( ready_to_send(v_Axi_out)  and counter < 40) ) then 
          send_data( v_Axi_out, counter);
          counter <= counter + 1;
          
        end if;
          push( v_Axi_out, Axi_out_m2s);
    end if;
    
    end process;
  
end architecture;
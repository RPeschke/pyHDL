library IEEE;
library UNISIM;
use IEEE.numeric_std.all;
use IEEE.std_logic_1164.all;
use UNISIM.VComponents.all;
use ieee.std_logic_unsigned.all;


entity tb_entity is 
end entity;



architecture rtl of tb_entity is

signal clkgen_clk : std_logic := '0'; 
signal maxCount : std_logic_vector(32 -1 downto 0) := 20; 
signal axiSource_Axi_out_m2s : axiStream_32_m2s := axiStream_32_m2s_null;
signal axiSource_Axi_out_s2m : axiStream_32_s2m := axiStream_32_s2m_null;
signal axP_Axi_in_m2s : axiStream_32_m2s := axiStream_32_m2s_null;
signal axP_Axi_in_s2m : axiStream_32_s2m := axiStream_32_s2m_null;
signal axFilter_Axi_in_m2s : axiStream_32_m2s := axiStream_32_m2s_null;
signal axFilter_Axi_in_s2m : axiStream_32_s2m := axiStream_32_s2m_null;
signal axFilter_Axi_out_m2s : axiStream_32_m2s := axiStream_32_m2s_null;
signal axFilter_Axi_out_s2m : axiStream_32_s2m := axiStream_32_s2m_null;

begin
clkgen : entity work.clk_generator port map ( 
      clk => clkgen_clk
  );
  axiSource : entity work.rollingCounter port map ( 
      Axi_out_m2s => axiSource_Axi_out_m2s, 
      Axi_out_s2m => axiSource_Axi_out_s2m,
      MaxCount => maxCount,
      clk => clkgen_clk
  );
  axP : entity work.axiPrint port map ( 
      Axi_in_m2s => axP_Axi_in_m2s, 
      Axi_in_s2m => axP_Axi_in_s2m,
      clk => clkgen_clk
  );
  axFilter : entity work.axiFilter port map ( 
      Axi_in_m2s => axFilter_Axi_in_m2s, 
      Axi_in_s2m => axFilter_Axi_in_s2m,
      Axi_out_m2s => axFilter_Axi_out_m2s, 
      Axi_out_s2m => axFilter_Axi_out_s2m,
      clk => clkgen_clk
  );
  ---------------------------------------------------------------------
  --  axFilter_Axi_in << axiSource_Axi_out
  axFilter_Axi_in_m2s <= axiSource_Axi_out_m2s;
  axiSource_Axi_out_s2m <= axFilter_Axi_in_s2m;
    ---------------------------------------------------------------------
  --  axP_Axi_in << axFilter_Axi_out
  axP_Axi_in_m2s <= axFilter_Axi_out_m2s;
  axFilter_Axi_out_s2m <= axP_Axi_in_s2m;
  
end architecture;
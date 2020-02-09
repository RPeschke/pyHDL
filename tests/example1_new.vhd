library IEEE;
library UNISIM;
use IEEE.numeric_std.all;
use IEEE.std_logic_1164.all;
use UNISIM.VComponents.all;
use ieee.std_logic_unsigned.all;


entity tb_entity is 
end entity;



architecture rtl of tb_entity is

--------------------------tb_entity-----------------
--------------------------clkgen-----------------
  signal clkgen_clk : std_logic := '0'; 
-------------------------- end clkgen-----------------
  signal maxCount : std_logic_vector(32 -1 downto 0) := 20; 
--------------------------pipe1-----------------
--------------------------pipe1_1_rollingCounter-----------------
  signal Axi_out_m2s : axiStream_32_m2s := axiStream_32_m2s_null;
  signal Axi_out_s2m : axiStream_32_s2m := axiStream_32_s2m_null;
-------------------------- end pipe1_1_rollingCounter-----------------
--------------------------pipe1_2_axiFilter-----------------
  signal Axi_in_m2s : axiStream_32_m2s := axiStream_32_m2s_null;
  signal Axi_in_s2m : axiStream_32_s2m := axiStream_32_s2m_null;
  signal Axi_out_m2s : axiStream_32_m2s := axiStream_32_m2s_null;
  signal Axi_out_s2m : axiStream_32_s2m := axiStream_32_s2m_null;
-------------------------- end pipe1_2_axiFilter-----------------
--------------------------pipe1_3_axiPrint-----------------
  signal Axi_in_m2s : axiStream_32_m2s := axiStream_32_m2s_null;
  signal Axi_in_s2m : axiStream_32_s2m := axiStream_32_s2m_null;
-------------------------- end pipe1_3_axiPrint-----------------
-------------------------- end pipe1-----------------
-------------------------- end tb_entity-----------------

begin
clkgen : entity work.clk_generator port map ( 
      clk => clkgen_clk
  );
  pipe1_1_rollingCounter : entity work.rollingCounter port map ( 
      Axi_out_m2s => Axi_out_m2s, 
      Axi_out_s2m => Axi_out_s2m,
      MaxCount => MaxCount,
      clk => clk
  );
    pipe1_2_axiFilter : entity work.axiFilter port map ( 
      Axi_in_m2s => Axi_in_m2s, 
      Axi_in_s2m => Axi_in_s2m,
      Axi_out_m2s => Axi_out_m2s, 
      Axi_out_s2m => Axi_out_s2m,
      clk => clk
  );
    pipe1_3_axiPrint : entity work.axiPrint port map ( 
      Axi_in_m2s => Axi_in_m2s, 
      Axi_in_s2m => Axi_in_s2m,
      clk => clk
  );
    ---------------------------------------------------------------------
  --  Axi_in << Axi_out
  Axi_in_m2s <= Axi_out_m2s;
  Axi_out_s2m <= Axi_in_s2m;
    ---------------------------------------------------------------------
  --  Axi_in << Axi_out
  Axi_in_m2s <= Axi_out_m2s;
  Axi_out_s2m <= Axi_in_s2m;
  
end architecture;
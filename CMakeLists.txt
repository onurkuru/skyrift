cmake_minimum_required(VERSION 3.16)

option(BUILD_VITA "Build for PS Vita (requires VitaSDK)" OFF)

if(BUILD_VITA)
  if(NOT DEFINED ENV{VITASDK})
    message(FATAL_ERROR "VITASDK env var not set. Install VitaSDK first (see README).")
  endif()
  set(CMAKE_TOOLCHAIN_FILE "$ENV{VITASDK}/share/vita.toolchain.cmake" CACHE PATH "toolchain file")
endif()

project(skyrift C)
set(CMAKE_C_STANDARD 99)

set(ASSETS
  door.png door-opened.png squirrel-idle.png squirrel-run.png squirrel-jump.png
  eagle.png frog-idle.png frog-jump.png opossum.png death.png gem.png cherry.png
  tileset.png back.png middle.png
  tree.png bush.png shrooms.png platform.png sign.png
)

if(BUILD_VITA)
  include("$ENV{VITASDK}/share/vita.cmake" REQUIRED)

  set(VITA_APP_NAME "Skyrift")
  set(VITA_TITLEID  "SKRF00001")
  set(VITA_VERSION  "01.00")

  add_executable(${PROJECT_NAME} src/main.c)

  find_package(SDL2 REQUIRED)
  target_include_directories(${PROJECT_NAME} PRIVATE ${SDL2_INCLUDE_DIRS})
  target_link_libraries(${PROJECT_NAME}
    SDL2::SDL2-static
    m
  )

  set(VPK_ASSET_ARGS "")
  foreach(a ${ASSETS})
    list(APPEND VPK_ASSET_ARGS FILE ${CMAKE_SOURCE_DIR}/assets/${a} assets/${a})
  endforeach()

  vita_create_self(${PROJECT_NAME}.self ${PROJECT_NAME})
  vita_create_vpk(${PROJECT_NAME}.vpk ${VITA_TITLEID} ${PROJECT_NAME}.self
    VERSION ${VITA_VERSION}
    NAME ${VITA_APP_NAME}
    FILE ${CMAKE_SOURCE_DIR}/sce_sys/icon0.png sce_sys/icon0.png
    ${VPK_ASSET_ARGS}
  )
else()
  add_executable(${PROJECT_NAME} src/main.c)

  find_package(SDL2 REQUIRED CONFIG)
  target_link_libraries(${PROJECT_NAME} SDL2::SDL2)
  if(NOT WIN32)
    target_link_libraries(${PROJECT_NAME} m)
  endif()

  # keep assets next to the binary so SDL_GetBasePath finds them
  add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory
      ${CMAKE_SOURCE_DIR}/assets $<TARGET_FILE_DIR:${PROJECT_NAME}>/assets
  )
endif()

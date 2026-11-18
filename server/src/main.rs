use voxelize::{
    Block, Chunk, ChunkStage, Registry, Resources, Server, Space, Vec3, VoxelAccess, Voxelize,
    World, WorldConfig,
};

const BASALT: u32 = 1;
const SLATE: u32 = 2;
const CINDER: u32 = 3;
const EMBER: u32 = 4;

struct EmberVault;

// One cell is one metre. The floor surface is at y=4.
fn block_at(x: i32, y: i32, z: i32) -> u32 {
    let radius = ((x as f32 + 0.5) / 24.0).powi(2) + ((z as f32 + 0.5) / 32.0).powi(2);
    let entrance = (-3..3).contains(&x) && (24..35).contains(&z);
    if radius > 1.12 && !entrance {
        return 0;
    }
    let ash = (x.div_euclid(3) * 17 + z.div_euclid(3) * 7 + y / 3).rem_euclid(11);
    let floor = if z < -17 && x.abs() < 11 { 5 } else { 4 };
    if y < floor {
        let ring = (x as f32 + 0.5).hypot(z as f32 + 0.5);
        return if (12.0..12.8).contains(&ring) || (radius > 0.93 && radius < 0.97) {
            CINDER
        } else if ash < 3 {
            SLATE
        } else {
            BASALT
        };
    }
    // Carved fire pillars frame the dais and mark the sides of the arena.
    for (px, pz) in [(8, -24), (17, -10), (19, 5), (13, 19)] {
        let d = (x.abs() - px).abs().max((z - pz).abs());
        if (d <= 2 && y < 6) || (d <= 1 && y < 10) {
            return if y == 9 {
                EMBER
            } else if y == 8 {
                CINDER
            } else {
                SLATE
            };
        }
        if d == 0 && y < 12 {
            return EMBER;
        }
    }
    if entrance && y < 10 {
        return 0;
    }
    let ceiling = 4 + (6.0 + 26.0 * (1.0 - radius).max(0.0).sqrt()).round() as i32;
    if radius > 1.0 || y >= ceiling {
        return if y < 12 && (x + z / 2).rem_euclid(13) < 2 {
            EMBER
        } else if ash < 4 {
            CINDER
        } else {
            BASALT
        };
    }
    0
}

impl ChunkStage for EmberVault {
    fn name(&self) -> String {
        "Ember Vault".to_owned()
    }

    fn process(&self, mut chunk: Chunk, _: Resources, _: Option<Space>) -> Chunk {
        let Vec3(x0, _, z0) = chunk.min;
        let Vec3(x1, _, z1) = chunk.max;
        for x in x0..x1 {
            for z in z0..z1 {
                for y in 0..39 {
                    let block = block_at(x, y, z);
                    if block != 0 {
                        chunk.set_voxel(x, y, z, block);
                    }
                }
            }
        }
        chunk
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let mut registry = Registry::new();
    registry.register_blocks(&[
        Block::new("Basalt").id(BASALT).build(),
        Block::new("Slate").id(SLATE).build(),
        Block::new("Cinder").id(CINDER).build(),
        Block::new("Ember")
            .id(EMBER)
            .red_light_level(15)
            .green_light_level(8)
            .blue_light_level(3)
            .build(),
    ]);
    let config = WorldConfig::new()
        .min_chunk([-2, -3])
        .max_chunk([1, 2])
        .max_height(64)
        .sub_chunks(4)
        .time_per_day(2400)
        .build();
    let mut world = World::new("ember-vault", &config);
    world.pipeline_mut().add_stage(EmberVault);
    let mut server = Server::new()
        .addr("127.0.0.1")
        .port(4100)
        .registry(&registry)
        .build();
    server.add_world(world).expect("unique world name");
    Voxelize::run(server).await
}

#[test]
fn arena_has_walkable_floor_and_flight_clearance() {
    assert_ne!(block_at(0, 3, 20), 0);
    assert!((4..36).all(|y| block_at(0, y, 0) == 0));
    assert_ne!(block_at(0, 36, 0), 0);
    assert_eq!(block_at(0, 7, 31), 0);
}
